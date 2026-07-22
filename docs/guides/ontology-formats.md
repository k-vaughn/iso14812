# Ontology File Formats and Annotations

## General

This repository maintains the ISO 14812 vocabulary using technologies chosen for version control, formal semantics, and automated website generation:

| Technology | Purpose |
|------------|---------|
| **GitHub** | Version control, reviews, issues, releases |
| **OWL 2** | Class/property semantics and imports |
| **W3C Turtle (`.ttl`)** | Authoritative serialization ([details](turtle.md)) |
| **`docs/python/ttl2mkdocs.py`** | Convert Turtle into Markdown, diagrams, and MkDocs navigation ([script README](../python/README.md)) |
| **Graphviz** | Render concept diagrams from generated DOT |
| **Material for MkDocs** | Build the public documentation site |

ISO 14812 is a **single vocabulary project** (`iso14812`) with one namespace and many modular Turtle files under `docs/`.

## Repository organization

| Artifact | Convention |
|----------|------------|
| GitHub repository | `ISO-TC204/iso14812` |
| Public site | `https://isotc204.org/iso14812` |
| Vocabulary namespace | `https://w3id.org/itsdata/vocab/` |
| Master Turtle file | `docs/itsVocabulary.ttl` |

Imported W3C vocabularies (RDF, RDFS, OWL, SKOS, Dublin Core, XSD, VANN, CC) are referenced by their standard IRIs via `PREFIX` declarations. They are not copied into this repository.

## Namespaces and prefixes

Declare only the prefixes needed for readability and diagram shortening. Typical prefixes in this project:

| Prefix | IRI |
|--------|-----|
| `:` (default) | `https://w3id.org/itsdata/vocab/` |
| `dcterms:` | `http://purl.org/dc/terms/` |
| `owl:` | `http://www.w3.org/2002/07/owl#` |
| `rdf:` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| `rdfs:` | `http://www.w3.org/2000/01/rdf-schema#` |
| `skos:` | `http://www.w3.org/2004/02/skos/core#` |
| `vann:` | `http://purl.org/vocab/vann/` |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` |
| `cc:` | `http://creativecommons.org/ns#` |

Each Turtle file **should** begin with `BASE <https://w3id.org/itsdata/vocab/>` and matching `PREFIX : <...>`.

## Ontology (module) annotations

### Master ontology (`itsVocabulary.ttl`)

Recommended annotations, in roughly this order:

| Annotation | Usage |
|------------|--------|
| `dcterms:title` | Site / vocabulary name |
| `dcterms:description` | Home-page summary (Markdown links allowed) |
| `dcterms:license` | Legal terms (CC BY 4.0 is used) |
| `cc:attributionName` | Attribution text |
| `vann:preferredNamespacePrefix` | Preferred short prefix (`itsVocab`) |
| `dcterms:creator` | Primary author(s) |
| `dcterms:issued` | Issue / publication date for this formalization |
| `dcterms:modified` | Last modification date |
| `owl:versionInfo` | Semantic version string |
| `owl:versionIRI` | Version IRI for the release |
| `rdfs:comment` | Optional human-readable version history notes |
| `owl:imports` | `core.ttl` and every top-level `*-group.ttl` |

### Group and pattern ontologies

| Annotation | Usage |
|------------|--------|
| `dcterms:title` | **Required** for navigation and page headings |
| `dcterms:modified` | Date of last edit to the module |
| `owl:imports` | Patterns import `core.ttl`; groups import their patterns (and optionally `core.ttl`) |
| `dcterms:description` / `skos:definition` | Optional module overview text |

## Annotations for terms (classes)

Prefer the following annotations on vocabulary classes. The website generator treats several of these specially (definition, labels, clause, notes, examples, history, source).

### Required / strongly expected

| Annotation | Usage |
|------------|--------|
| `skos:prefLabel` | Preferred term; used as the page title and primary display name. One per language. |
| `skos:definition` | Normative definition. Prefer markdown links to other terms where useful. One primary definition per language. |
| `:clause` | Clause number in the ISO vocabulary structure (for example `"3.6.1.4"`). Declared in `core.ttl`. |

### Recommended as needed

| Annotation | Usage |
|------------|--------|
| `:altPrefLabel` | Alternative preferred term (project-specific; declared in `core.ttl`) |
| `skos:altLabel` | Admitted term |
| `skos:hiddenLabel` | Deprecated or hidden term |
| `skos:note` | Informative note to entry; repeatable |
| `skos:example` | EXAMPLE material; repeatable |
| `skos:historyNote` | Introduction / change history relative to ISO editions |
| `dcterms:source` | Bibliographic or normative source text |
| `rdfs:subClassOf` | Hierarchical specialization (URI or restriction) |
| `owl:disjointWith` | Disjointness axioms when required |

### Clause numbering rules

Patterns and groups are validated when the site is generated:

- All terms in a **pattern** should share the same parent clause (for example `3.7.6.1` … `3.7.6.6` → parent `3.7.6`).
- Final segments under that parent should be **contiguous** (no gaps or duplicates).
- Patterns within a **group** should likewise share a common root and use sequential numbering at the pattern level.

Warnings for root mismatches or missing clause numbers are reprinted in the run summary at the end of `ttl2mkdocs.py`.

## Annotations for properties

Object and datatype properties are typically declared in `core.ttl` or in the pattern that introduces them. Recommended:

| Annotation | Usage |
|------------|--------|
| `rdfs:label` | Human-readable property name for diagrams and tables |
| `rdfs:domain` / `rdfs:range` | When appropriate for documentation |
| `skos:definition` | If the property itself needs a vocabulary-style definition |

Project-specific annotation properties defined in `core.ttl`:

| Property | Purpose |
|----------|---------|
| `:clause` | Vocabulary clause number on terms |
| `:altPrefLabel` | Alternative preferred label on terms |

## SHACL

This vocabulary repository currently focuses on OWL semantics and documentation generation. SHACL constraint files are **not** part of the standard module naming scheme here. If validation shapes are introduced later, prefer a clear suffix (for example `*-shacl.ttl`) and keep constraints separate from definitional OWL, as described in [turtle.md](turtle.md).

## Formatting policies for definitions

- Write definitions so they work as ISO vocabulary entries (genus + differentia where practical).
- When referring to other defined terms, use markdown links that the tooling and site can resolve (for example `[road vehicle](road vehicle.md)`).
- Keep one primary `skos:definition` per language; put elaboration in `skos:note` or `skos:example`.
- Record edition provenance in `skos:historyNote` (for example “Introduced in ISO/TS 14812:2022”).
