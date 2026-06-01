# ontology_processor_ttl.py
"""Load modular ITS vocabulary Turtle files and build collection metadata for MkDocs."""

from __future__ import annotations

import logging
import os
import re
import textwrap
import traceback
from pathlib import Path
from urllib.parse import urljoin

from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef
from rdflib.namespace import DC, DCTERMS, SKOS

from utils import get_label, get_ontology_metadata, get_qname, insert_spaces, update_concept_registry

log = logging.getLogger("ttl2mkdocs")

BASE = "https://w3id.org/itsdata/vocab/"
MASTER_FILE = "itsVocabulary.ttl"
IMPORT_REF = re.compile(r"<\s*([^>]+)\s*>")
ONTOLOGY_NAME = re.compile(r":([\w-]+)\s+a\s+owl:Ontology")
ONTOLOGY_TITLE = re.compile(r'dcterms:title\s+"([^"]+)"@en')


def parse_ontology_description(path: Path) -> str | None:
    match = re.search(r'dcterms:description\s+"([^"]+)"@en', path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def parse_imports(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    start = text.find("owl:imports")
    if start == -1:
        return []
    remainder = text[start:]
    end = len(remainder)
    for match in re.finditer(r"\.\s*(?:\n|$)", remainder):
        end = match.start()
        break
    return IMPORT_REF.findall(remainder[:end])


def parse_ontology_local_name(path: Path) -> str | None:
    match = ONTOLOGY_NAME.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def parse_ontology_title(path: Path) -> str | None:
    match = ONTOLOGY_TITLE.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def classify_module(filename: str) -> str:
    if filename == MASTER_FILE:
        return "master"
    if filename == "terms-group.ttl":
        return "terms"
    if filename == "core.ttl":
        return "core"
    if filename.endswith("-group.ttl"):
        return "group"
    if filename.endswith("-pattern.ttl"):
        return "pattern"
    return "other"


def import_module_name(import_path: str) -> str | None:
    match = re.match(r"(.+)-(group|pattern)\.ttl$", import_path)
    return match.group(1) if match else None


def collection_title(name: str) -> str:
    title = insert_spaces(name)
    if title.endswith(" Terms"):
        return title[0].upper() + title[1:]
    if title.endswith("Terms"):
        return title[:-5] + " Terms"
    return title[0].upper() + title[1:] if title else title


def collect_import_closure(start: Path, docs_dir: Path) -> list[Path]:
    seen: set[Path] = set()
    queue = [start.resolve()]
    ordered: list[Path] = []
    while queue:
        path = queue.pop(0)
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        ordered.append(path)
        for imp in parse_imports(path):
            if imp.startswith("http"):
                continue
            child = (docs_dir / imp).resolve()
            if child not in seen:
                queue.append(child)
    return ordered


def discover_modules(docs_dir: Path) -> dict[str, dict]:
    master = docs_dir / MASTER_FILE
    if not master.is_file():
        raise FileNotFoundError(f"{MASTER_FILE} not found in {docs_dir}")

    modules: dict[str, dict] = {}
    for path in collect_import_closure(master, docs_dir):
        local_name = parse_ontology_local_name(path)
        if not local_name:
            continue
        modules[local_name] = {
            "path": path,
            "imports": parse_imports(path),
            "title": parse_ontology_title(path),
            "kind": classify_module(path.name),
            "order": 99999,
        }

    def assign_order(local_name: str, order: int) -> None:
        if local_name not in modules:
            return
        modules[local_name]["order"] = order
        child_idx = 0
        for imp in modules[local_name]["imports"]:
            child = import_module_name(imp)
            if child and child in modules:
                assign_order(child, child_idx)
                child_idx += 1

    if "terms" in modules:
        assign_order("terms", 0)

    return modules


def clause_sort_key(clause) -> tuple:
    if clause is None:
        return (99999,)
    try:
        return tuple(int(part) for part in str(clause).split("."))
    except ValueError:
        return (99999,)


def collect_pattern_classes(
    pattern_path: Path,
    graph: Graph,
    ns: str,
    ontology_name: str,
) -> list[tuple[str, str, str, tuple]]:
    local = Graph()
    local.parse(pattern_path, format="turtle")
    clause_prop = URIRef(ns + "clause")
    classes: list[tuple[str, str, str, tuple]] = []
    for cls in local.subjects(RDF.type, OWL.Class):
        if cls == OWL.Thing:
            continue
        label = get_label(graph, cls) or get_label(local, cls)
        if not label or not label.strip():
            continue
        clause = graph.value(cls, clause_prop) or local.value(cls, clause_prop)
        classes.append((str(cls), label, ontology_name, clause_sort_key(clause)))
    classes.sort(key=lambda item: (item[3], item[1].lower()))
    return classes


def build_global_patterns(
    modules: dict[str, dict],
    pattern_classes: dict[str, list],
) -> dict[str, dict]:
    global_patterns: dict[str, dict] = {}
    for local_name, mod in modules.items():
        if mod["kind"] not in {"terms", "group", "pattern"}:
            continue
        coll_uri = BASE + local_name
        gp = {
            "name": mod.get("title") or collection_title(local_name),
            "order": mod.get("order", 99999),
            "subcollections": [],
            "classes": pattern_classes.get(local_name, []),
        }
        for imp in mod["imports"]:
            child = import_module_name(imp)
            if child and child in modules and modules[child]["kind"] in {"group", "pattern"}:
                gp["subcollections"].append(BASE + child)
        global_patterns[coll_uri] = gp
    return global_patterns


def parse_concept_registry(script_dir: str) -> dict:
    root_dir = os.getcwd()
    docs_dir = os.path.join(root_dir, "docs")
    registry_path = os.path.join(docs_dir, "concept_registry.md")
    if not os.path.exists(registry_path):
        with open(registry_path, "w", encoding="utf-8") as f:
            f.write("| uri | name | description |\n|-----|----------|------|\n")
        log.info("Created new concept_registry.md in %s", script_dir)
        return {}

    registry: dict = {}
    content = open(registry_path, encoding="utf-8").read()
    in_table = False
    headers = None
    for line in content.splitlines():
        if line.strip().startswith("|"):
            if not in_table:
                headers = [h.strip().lower() for h in line.split("|") if h.strip()]
                in_table = True
            elif headers and not line.strip().startswith("|---"):
                values = [v.strip() for v in line.split("|") if v.strip()]
                if len(values) < 2:
                    continue
                try:
                    uri = values[headers.index("uri")]
                    name_match = re.search(r"\[(.*?)\]", values[headers.index("name")])
                    if not name_match:
                        continue
                    name = name_match.group(1)
                    description = (
                        values[headers.index("description")]
                        if "description" in headers and len(values) > headers.index("description")
                        else ""
                    )
                    registry[uri] = {"name": name, "type": "class", "description": description}
                except ValueError:
                    continue
    return registry


def load_vocabulary_graph(module_paths: list[Path]) -> Graph:
    graph = Graph()
    graph.bind("", URIRef(BASE))
    for path in module_paths:
        graph.parse(path, format="turtle")
        log.debug("Loaded %s (%d triples so far)", path.name, len(graph))
    return graph


def build_prefix_map(graph: Graph, ns: str) -> dict[str, str]:
    prefix_map = {str(uri): f"{prefix}:" for prefix, uri in graph.namespaces()}
    if ns not in prefix_map:
        prefix_map[ns] = ":"
    return prefix_map


def process_vocabulary(
    docs_dir: Path | str,
    errors: list,
    ontology_info: dict,
) -> tuple:
    """Load modular TTL vocabulary files and return graph metadata for MkDocs generation."""
    docs_dir = Path(docs_dir)
    master_path = (docs_dir / MASTER_FILE).resolve()
    try:
        modules = discover_modules(docs_dir)
    except FileNotFoundError as exc:
        errors.append(str(exc))
        log.error(str(exc))
        return None, None, None, None, None, None

    module_paths = [mod["path"] for mod in modules.values()]
    try:
        graph = load_vocabulary_graph(module_paths)
        if len(graph) == 0:
            raise ValueError("RDF graph is empty after loading vocabulary TTL files")
        log.info(
            "Loaded vocabulary from %d TTL modules (%d triples)",
            len(module_paths),
            len(graph),
        )
    except Exception as exc:
        error_msg = f"Failed to load vocabulary TTL files: {exc}\n{traceback.format_exc()}"
        errors.append(error_msg)
        log.error(error_msg)
        return None, None, None, None, None, None

    ns = BASE
    prefix_map = build_prefix_map(graph, ns)
    ontology_name = master_path.stem

    script_dir = os.path.dirname(os.path.realpath(__file__))
    registry = parse_concept_registry(script_dir)

    for uri, info in registry.items():
        if info["type"] == "object_property":
            graph.add((URIRef(uri), RDF.type, OWL.ObjectProperty))
        elif info["type"] == "datatype_property":
            graph.add((URIRef(uri), RDF.type, OWL.DatatypeProperty))

    new_concepts: dict = {}
    for cls in graph.subjects(RDF.type, OWL.Class):
        uri = str(cls)
        if uri not in registry and uri not in new_concepts:
            description = (
                graph.value(cls, SKOS.definition)
                or graph.value(cls, DCTERMS.description)
                or graph.value(cls, DC.description)
                or graph.value(cls, RDFS.comment)
                or "-"
            )
            new_concepts[uri] = {
                "name": get_label(graph, cls),
                "type": "class",
                "description": str(description) if isinstance(description, Literal) else description,
            }

    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for prop in graph.subjects(RDF.type, prop_type):
            uri = str(prop)
            if uri not in registry and uri not in new_concepts:
                description = (
                    graph.value(prop, SKOS.definition)
                    or graph.value(prop, DCTERMS.description)
                    or graph.value(prop, DC.description)
                    or graph.value(prop, RDFS.comment)
                    or "-"
                )
                new_concepts[uri] = {
                    "name": get_label(graph, prop),
                    "type": "object_property" if prop_type == OWL.ObjectProperty else "datatype_property",
                    "description": str(description) if isinstance(description, Literal) else description,
                }

    for uri, info in new_concepts.items():
        if uri not in registry:
            registry[uri] = info
    update_concept_registry(script_dir, registry)

    dc_title = parse_ontology_title(master_path) or get_ontology_metadata(graph, ns, DCTERMS.title) or "Untitled Ontology"
    dc_description = (
        parse_ontology_description(master_path)
        or get_ontology_metadata(graph, ns, DCTERMS.description)
        or get_ontology_metadata(graph, ns, DC.description)
        or get_ontology_metadata(graph, ns, RDFS.comment)
        or "-"
    )
    if dc_description != "-":
        dc_description = textwrap.dedent(dc_description).strip()

    ontology_info[str(master_path)] = {
        "title": dc_title,
        "description": dc_description,
        "patterns": set(),
        "non_pattern_classes": set(),
        "ontology_name": ontology_name,
    }

    pattern_classes: dict[str, list] = {}
    patterned_labels: set[str] = set()
    for local_name, mod in modules.items():
        if mod["kind"] != "pattern":
            continue
        classes = collect_pattern_classes(mod["path"], graph, ns, ontology_name)
        pattern_classes[local_name] = classes
        ontology_info[str(master_path)]["patterns"].add(
            mod.get("title") or collection_title(local_name)
        )
        for _, label, _, _ in classes:
            patterned_labels.add(label)

    global_patterns = build_global_patterns(modules, pattern_classes)

    classes = set(graph.subjects(RDF.type, OWL.Class)) - {OWL.Thing}
    local_classes = [cls for cls in classes if urljoin(ns, str(cls)).startswith(ns)]
    log.info("Found %d local classes in namespace %s", len(local_classes), ns)

    non_pattern = {
        get_label(graph, cls)
        for cls in local_classes
        if get_label(graph, cls) not in patterned_labels and get_label(graph, cls) != "ITSThing"
    }
    ontology_info[str(master_path)]["non_pattern_classes"] = non_pattern

    prop_map = {}
    for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
        prop_map[get_qname(graph, prop, ns, prefix_map)] = prop
    for prop in graph.subjects(RDF.type, OWL.DatatypeProperty):
        prop_map[get_qname(graph, prop, ns, prefix_map)] = prop

    return graph, ns, prefix_map, classes, local_classes, prop_map, global_patterns
