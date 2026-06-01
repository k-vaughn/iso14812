import os
import logging
import yaml
import re
import traceback
from collections import defaultdict
from rdflib import Graph, XSD, Literal, URIRef, OWL, RDFS, RDF
from rdflib.namespace import DCTERMS, SKOS
from utils import get_label, get_property_info, get_qname, get_first_literal, get_class_expression_str, insert_spaces, class_restrictions, iter_annotations, DESC_PROPS, get_ontology_for_uri, fauxClass, get_filename, TERMS_SUBDIR, term_nav_path, term_page_link, term_page_filename, diagram_path_from_terms

log = logging.getLogger("ttl2mkdocs")

class SafeMkDocsLoader(yaml.SafeLoader):
    """Custom YAML loader to handle MkDocs-specific python/name tags."""
    def ignore_python_name(self, node):
        """Treat python/name tags as strings."""
        return self.construct_scalar(node)

yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/name:material.extensions.emoji.twemoji', SafeMkDocsLoader.ignore_python_name)
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/name:pymdownx.superfences.fence_code_format', SafeMkDocsLoader.ignore_python_name)
yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/name:material.extensions.emoji.to_svg', SafeMkDocsLoader.ignore_python_name)

def get_specializations(g: Graph, cls: URIRef, global_all_classes: set, ns: str, prefix_map: dict, ns_to_ontology: dict) -> list:
    """Find all subclasses (direct and indirect) of the given class."""
    specializations = []
    visited = set()
    def collect_subclasses(c):
        if c in visited:
            return
        visited.add(c)
        for s in g.subjects(RDFS.subClassOf, c):
            if isinstance(s, URIRef) and s != c:
                cls_name = get_first_literal(g, s, [RDFS.label]) or str(s).split('/')[-1].split('#')[-1]
                ont = get_ontology_for_uri(str(s), ns_to_ontology)
                if cls_name in global_all_classes and ont:
                    desc = get_first_literal(g, s, [DCTERMS.description]) or ""
                    specializations.append((cls_name, desc, ont))
                collect_subclasses(s)
    collect_subclasses(cls)
    log.debug(f"Specializations for {cls}: {specializations}")
    return sorted(specializations, key=lambda x: x[0].lower())

def get_used_by(cls: str, prop_list: list):
    used_by = []
    log.debug(f"length of prop_list: {len(prop_list)}")
    for item in prop_list:
        if len(item) != 3:
            continue
        using_cls, prop_name, target_class = item
        if target_class == cls:
            used_by.append((using_cls, prop_name))
            log.debug(f"Found usage: {using_cls} uses {cls} via {prop_name}")
    return sorted(set(used_by))

def generate_prop_list(g: Graph, global_all_class_uris: set, ns: str, prefix_map: dict):
    """Generate property list for all classes."""
    prop_list = []
    for cls in sorted(global_all_class_uris):
        cls_uri = URIRef(cls)
        # Formalization section with superclasses and disjoints
        for restriction in g.objects(cls_uri, RDFS.subClassOf):
            if (restriction, RDF.type, OWL.Restriction) in g:
                prop = g.value(restriction, OWL.onProperty)
                target_class = g.value(restriction, OWL.onClass)
                if prop and target_class:
                    prop_name, _, _ = get_property_info(g, prop, ns, prefix_map)
#                    target_id, _, _, target_qname, reflexive, _ = get_target_info(g, target_expr, cls_name, ns, prefix_map)
#                   range_name = get_class_expression_str(g, range_expr, ns, prefix_map)
                    prop_list.append((str(cls), prop_name, get_label(g, target_class)))
        # Collect direct superclasses
        for super_cls in g.objects(cls_uri, RDFS.subClassOf):
            if isinstance(super_cls, URIRef) and super_cls != OWL.Thing:
                super_name = get_qname(g, super_cls, ns, prefix_map)
                prop_list.append((str(cls), "subClassOf", super_name))
        # Collect disjoint classes
        for disjoint_cls in g.objects(cls_uri, OWL.disjointWith):
            if isinstance(disjoint_cls, URIRef):
                disjoint_name = get_qname(g, disjoint_cls, ns, prefix_map)
                prop_list.append((str(cls), "disjointWith", disjoint_name))
    log.debug(f"Generated property list: {prop_list}")
    return prop_list

def generate_markdown(g: Graph, cls: URIRef, cls_name: str, global_patterns: dict, global_all_classes: set, ns: str, file_path: str, errors: list, prefix_map: dict, prop_list: list, ns_to_ontology: dict, class_to_onts: dict):
    """Generate Markdown file for a class, including all superclasses and disjoint statements in Formalization."""
    docs_dir = os.path.dirname(file_path)
    terms_dir = os.path.join(docs_dir, TERMS_SUBDIR)
    os.makedirs(terms_dir, exist_ok=True)
    filename = os.path.join(terms_dir, term_page_filename(cls_name))
    
    log.debug(f"Writing {filename} for class {cls_name} ({cls})")
    # Check if this is a pattern class
    is_pattern = cls_name in global_patterns
    log.info(f"Generating Markdown for {'pattern' if is_pattern else 'non-pattern'} class: {cls_name}")

    if is_pattern:
        log.warning(f"Generating pattern class Markdown for {cls_name}")
        # Pattern class Markdown
#        title = f"# {insert_spaces(cls_name)}\n\n"
#        desc = get_first_literal(g, cls, [SKOS.definition]) or ""
#        log.debug(f"Pattern {cls_name} description: {desc}")
#        top_desc = f"{desc}\n\n" if desc else ""
#        members_md = "It consists of the following classes:\n\n"
#        member_tuples = global_patterns[cls_name]["classes"]
#        for mem_cls, mem_ont in sorted(member_tuples, key=lambda x: x[0].lower()):
#            if mem_cls == 'ITSThing':
#                continue
#            display_mem = insert_spaces(mem_cls)
#            if len(class_to_onts[mem_cls]) > 1:
#                display_mem += f" ({mem_ont})"
#            members_md += f"- [{display_mem}]({mem_ont}__{mem_cls}.md)\n"
#        content = title + top_desc + members_md
    else:
        # Non-pattern class Markdown
        title = f"# {cls_name}\n\n"
        alt_labels_md = ""
        alt_pref_label_pre = URIRef(ns + 'altPrefLabel')
        alt_pref_labels = list(g.objects(cls, alt_pref_label_pre))
        if alt_pref_labels:
            for alt_pref_label in alt_pref_labels:
                alt_labels_md += f"Alternative preferred term: {str(alt_pref_label)}\n\n"
        alt_labels = list(g.objects(cls, SKOS.altLabel))
        if alt_labels:
            for alt_label in alt_labels:
                alt_labels_md += f"Admitted term: {str(alt_label)}\n\n"
        hidden_labels = list(g.objects(cls, SKOS.hiddenLabel))
        if hidden_labels:
            for hidden_label in hidden_labels:
                alt_labels_md += f"Deprecated term: {str(hidden_label)}\n\n"
        desc = get_first_literal(g, cls, [SKOS.definition]) or ""
        log.debug(f"Class {cls_name} description: {desc}")
        top_desc = f"{desc}\n\n" if desc else ""
        notes = list(g.objects(cls, SKOS.note))
        note_md = ""
        if notes:
            for i, note in enumerate(notes, start=1):
                note_md += f"Note {i} to entry: {str(note)}\n\n"
        examples = list(g.objects(cls, SKOS.example))
        example_md = ""
        if examples:
            if len(examples) == 1:
                example_md += f"EXAMPLE: {str(examples[0])}\n\n"
            else:
                for i, example in enumerate(examples, start=1):
                    example_md += f"Example {i}: {str(example)}\n\n"
        sources = list(g.objects(cls, DCTERMS.source))
        source_md = ""
        if sources:
            for source in sources:
                source_md += f"Source: {str(source)}\n\n"
        clause_pre = URIRef(ns + 'clause')
        clause_md = f"Clause: {get_first_literal(g, cls, [clause_pre])}\n\n" if get_first_literal(g, cls, [clause_pre]) else ""
        history_md = ""
        historyNotes = list(g.objects(cls, SKOS.historyNote))
        if historyNotes:
            for hist_note in historyNotes:
                history_md += f"History note: {str(hist_note)}\n\n"
        diagram_line = f"<object type=\"image/svg+xml\" data=\"{diagram_path_from_terms(cls_name, 'dot.svg')}\">\n"
        diagram_line += f"    <img alt=\"{cls_name} Diagram\" src=\"{diagram_path_from_terms(cls_name, 'dot.png')}\" /> <!-- Fallback for non-SVG browsers -->\n"
        diagram_line += "</object>\n\n"
        
        # Specializations section
        specializations = get_specializations(g, cls, global_all_classes, ns, prefix_map, ns_to_ontology)
        specializations_md = ""
        if specializations:
            specializations_md += f"## Specializations of {cls_name}\n\n"
            specializations_md += "| Class | Description |\n"
            specializations_md += "|-------|-------------|\n"
            for spec_cls, spec_desc, spec_ont in specializations:
                display_spec = insert_spaces(spec_cls)
                if len(class_to_onts[spec_cls]) > 1:
                    display_spec += f" ({spec_ont})"
                link = term_page_link(spec_cls)
                specializations_md += f"| [{display_spec}]({link}) | {spec_desc} |\n"
            specializations_md += "\n"
        else:
            log.debug(f"No specializations found for {cls_name}")
        
        # Formalization section with superclasses and disjoints
        restr_rows = class_restrictions(g, cls, ns, prefix_map)
        # Collect direct superclasses
        superclasses = []
        for super_cls in g.objects(cls, RDFS.subClassOf):
            if isinstance(super_cls, URIRef) and super_cls != OWL.Thing:
                super_name = get_qname(g, super_cls, ns, prefix_map)
                superclasses.append(("subClassOf", super_name))
        # Collect disjoint classes
        disjoints = []
        for disjoint_cls in g.objects(cls, OWL.disjointWith):
            if isinstance(disjoint_cls, URIRef):
                disjoint_name = get_qname(g, disjoint_cls, ns, prefix_map)
                disjoints.append(("disjointWith", disjoint_name))
        # Combine with restrictions from class_restrictions
        formalization_rows = sorted(restr_rows + superclasses + disjoints, key=lambda x: x[0].lower())
        formalization_md = ""
        if formalization_rows:
            formalization_md += f"## Relationships for {cls_name}\n\n"
            formalization_md += "| Property | Constraint |\n"
            formalization_md += "|----------|------------|\n"
            for prop, constr in formalization_rows:
                log.debug(f"Restriction for {cls_name}: ({prop}, '{constr}')")
                formalization_md += f"| {prop} | {constr} |\n"
            formalization_md += "\n"
        
        # Used by section
        used_by = get_used_by(get_label(g, cls), prop_list)
        used_by_md = ""
        if used_by:
            used_by_md += f"## References to {cls_name}\n\n"
            used_by_md += "| Referencing Term | Type of Reference |\n"
            used_by_md += "|------------------|-------------------|\n"
            for using_cls, used_prop in used_by:
                using_uri = URIRef(using_cls)
                using_label = get_label(g, using_uri)
#                display_used = insert_spaces(using_cls)
                used_by_md += f"| [{using_label}]({term_page_link(using_label)}) | {used_prop} |\n"
            used_by_md += "\n"
        
        # Other annotations
        other_annot_md = ""
        annotations = list(iter_annotations(g, cls, ns, prefix_map))
        for pred, val in sorted(annotations):
            if pred=='altPrefLabel' or pred=='clause' or pred=='dcterms::source' or pred=='skos::altLabel' or pred=='skos::definition' or pred=='skos::example' or pred=='skos::hiddenLabel' or pred=='skos::historyNote' or pred=='skos::note' or pred=='skos::prefLabel':
                continue  # Already handled
            else:
                other_annot_md += f"| {pred} | {val} |\n"
        log.debug(f"Other annotations for {cls_name}: {other_annot_md}")
        if other_annot_md != "":
            other_annot_head = "## Other annotations\n\n"
            other_annot_head += "| Annotation | Value |\n"
            other_annot_head += "|------------|-------|\n"
            other_annot_md = other_annot_head + other_annot_md + "\n"
        
        content = title + top_desc + diagram_line + clause_md + alt_labels_md + example_md + note_md + source_md + history_md + specializations_md + formalization_md + used_by_md + other_annot_md

    # Write Markdown file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        log.debug("Generated Markdown file: %s", filename)
    except Exception as e:
        error_msg = f"Error writing Markdown for {cls_name} from {file_path}: {str(e)}\n{traceback.format_exc()}"
        errors.append(error_msg)
        log.error(error_msg)
        raise

def update_mkdocs_nav(mkdocs_path: str, global_patterns: dict, errors: list, class_to_onts: dict, ontology_info: dict, input_file: str, local_classes: set, g: Graph, ns: str):
    """Update mkdocs.yml navigation with file > pattern > class or file > class structure."""
    try:
        with open(mkdocs_path, 'r', encoding="utf-8") as f:
            config = yaml.load(f, Loader=SafeMkDocsLoader)
    except Exception as e:
        error_msg = f"Error reading mkdocs.yml: {str(e)}\n{traceback.format_exc()}"
        errors.append(error_msg)
        log.error(error_msg)
        raise

    new_nav = [{"Home": "index.md"}, {"Alphabetical Listing": "concept_registry.md"}]
    
    file_path = input_file
    ontology_name = ontology_info[file_path]["ontology_name"]
    # Find the "Terms" top-level collection (adjust IRI if needed)
    terms_coll_str = None
    for coll_str, gp in global_patterns.items():
        if gp["name"].lower() == "terms":  # or exact match: gp["name"] == "Terms"
            terms_coll_str = coll_str
            break

    if terms_coll_str:
        # Get direct members of "Terms" (sub-collections + classes)
        terms_gp = global_patterns[terms_coll_str]

        # Build the nav directly from Terms' children (skip showing "Terms")
        top_level_items = []

        # 1. Sub-collections of Terms
        for sub_coll_str in terms_gp.get("subcollections", []):
            log.info(f"Processing sub-collection for nav: {sub_coll_str}")
            if sub_coll_str in global_patterns:
                sub_gp = global_patterns[sub_coll_str]
                display_name = insert_spaces(sub_gp["name"])
                sub_nav = build_sub_nav(sub_coll_str, global_patterns, class_to_onts, ontology_name)
                log.debug(f"Built sub-nav for {display_name}: {sub_nav}")
                if sub_nav:
                    top_level_items.append({display_name: sub_nav})

        # 2. Direct classes that are members of Terms (not in any sub-collection)
        direct_classes = []
        for cls_data in terms_gp.get("classes", []):
            log.info(f"Processing direct class for nav: {cls_data}")
            cls_str, cls_name, ont, cls_order = cls_data
            # Only include classes that are not members of any sub-collection
            is_in_sub = False
            for sub_coll_str in terms_gp["subcollections"]:
                sub_gp = global_patterns.get(sub_coll_str, {})
                if any(c[0] == cls_str for c in sub_gp.get("classes", [])):
                    is_in_sub = True
                    break
            if not is_in_sub and not fauxClass(cls_name):
                direct_classes.append((cls_name, ont, cls_order))

        # Sort direct classes by order, then name
        direct_classes.sort(key=lambda x: (x[2], x[0].lower()))
        for cls_name, ont, _ in direct_classes:
            display_cls = insert_spaces(cls_name)
            top_level_items.append({display_cls: term_nav_path(cls_name)})
            log.info(f"Added top-level class to nav: {cls_name} ({display_cls})")

        # Add all top-level items to nav
        new_nav.extend(top_level_items)
        config["nav"] = new_nav

    else:
        log.warning("Top-level 'Terms' collection not found – falling back to all patterns")    

    try:
        with open(mkdocs_path, 'w', encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    except Exception as e:
        error_msg = f"Error writing mkdocs.yml: {str(e)}\n{traceback.format_exc()}"
        errors.append(error_msg)
        log.error(error_msg)
        raise

def generate_index(docs_dir: str, input_file: str, ontology_info: dict, global_patterns: dict, errors: list, class_to_onts: dict):
    """Generate index.md file."""
    index_path = os.path.join(docs_dir, "index.md")
    index_content = ""

    file_path = input_file
    if file_path not in ontology_info:
        error_msg = f"Skipping index.md generation for {file_path} due to earlier processing failure"
        errors.append(error_msg)
        log.error(error_msg)
        return
    filename = os.path.basename(file_path)
    title = ontology_info[file_path]["title"]
    description = ontology_info[file_path]["description"]
    patterns = sorted(ontology_info[file_path]["patterns"], key=str.lower)
    non_pattern_classes = sorted(ontology_info[file_path]["non_pattern_classes"], key=str.lower)
    index_content += f"# {title}\n\n"
    if description:
        index_content += f"{description}\n\n"
    index_content += f"\nThe formal definition of the terms is available in [{os.path.splitext(filename)[1][1:].upper()} Syntax]({filename}).\n"

    # Write index.md
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        log.info("Generated index.md at %s", index_path)
    except Exception as e:
        error_msg = f"Error writing index.md: {str(e)}\n{traceback.format_exc()}"
        errors.append(error_msg)
        log.error(error_msg)
        raise

def build_sub_nav(coll_str: str, global_patterns: dict, class_to_onts: dict, ontology_name: str) -> list:
    if coll_str not in global_patterns:
        return []
    gp = global_patterns[coll_str]
    sub_nav = []
    items = []
    for sub_coll in gp["subcollections"]:
        sub_gp = global_patterns.get(sub_coll, {})
        sub_order = sub_gp.get("order", 99999)
        items.append(("coll", sub_coll, sub_order))
    for cls_data in gp["classes"]:
        cls_str, cls_name, ont, cls_order = cls_data
        items.append(("cls", (cls_name, ont), cls_order))
    # Sort by order, then name
    items.sort(key=lambda x: (x[2], global_patterns[x[1]]["name"].lower() if x[0] == "coll" else x[1][0].lower()))
    for it_type, it_val, _ in items:
        if it_type == "coll":
            sub_coll_str = it_val
            sub_gp = global_patterns[sub_coll_str]
            display_pat = insert_spaces(sub_gp["name"])
            sub_sub_nav = build_sub_nav(sub_coll_str, global_patterns, class_to_onts, ontology_name)
            if sub_sub_nav:
                sub_nav.append({display_pat: sub_sub_nav})
        else:
            cls_name, ont = it_val
            display_mem = insert_spaces(cls_name)
            sub_nav.append({display_mem: term_nav_path(cls_name)})
    return sub_nav