# ISO 14812 Vocabulary Ontology — Contributor Guide

This guide explains how the ISO 14812 Intelligent Transport Systems (ITS) vocabulary is maintained as a formal ontology and published as a website. It is aimed at editors, reviewers, and developers working in this repository.

Related pages:

- [Naming conventions](naming-conventions.md)
- [Ontology file formats and annotations](ontology-formats.md)
- [Turtle serialization](turtle.md)
- [Website generation scripts](../python/README.md)

The public site is at [https://isotc204.org/iso14812](https://isotc204.org/iso14812). The normative content is periodically standardized as [ISO 14812](https://www.iso.org/standard/85041.html); this GitHub project is used for collaborative maintenance and change history.

## What is an ontology?

An ontology is a formal representation of knowledge within a domain: the concepts (classes), relationships and attributes (properties), and rules that connect them. In this project the vocabulary is encoded in OWL/RDF/TTL so that:

- each term has a stable IRI and machine-readable definition;
- hierarchical and associative relationships can be expressed explicitly;
- diagrams and documentation can be generated consistently from the same source.

## Why maintain the vocabulary as an ontology?

Documenting ISO 14812 as an ontology supports:

- **Shared meaning** — preferred terms, admitted terms, definitions, and notes stay aligned across standards and implementations.
- **Traceability** — each concept carries a clause number (`:clause`) that maps to the published vocabulary structure.
- **Interoperability** — other ITS ontologies and data models can import or reference these concepts by IRI.
- **Automation** — Turtle sources drive MkDocs pages, Graphviz diagrams, and navigation without hand-maintaining hundreds of HTML pages.
- **Standards process** — from edition 3 onward, draft content for the ISO deliverable is generated from this ontology.

## How this relates to data models and interface standards

- **Vocabulary / ontology** — defines *what terms mean* and how concepts relate (semantics).
- **Data models and interface standards** — define *how data is structured and exchanged* (syntax, fields, messages, APIs).

The ontology informs those models: a definition such as “road vehicle” should mean the same thing whether it appears in a message schema, a database design, or a regulatory text. Interface standards remain free to choose encodings; the ontology supplies the shared conceptual layer.

## How the ontology is documented

| Layer | Role in this project |
| ----- | -------------------- |
| **OWL / RDF (Turtle)** | Authoritative definition of classes, properties, imports, and annotations |
| **SKOS / Dublin Core annotations** | Human-facing definitions, labels, notes, examples, provenance |
| **Clause numbers** | Alignment with the published ISO vocabulary structure |
| **MkDocs + Material** | Human-readable website |
| **Graphviz diagrams** | Concept diagrams derived from class relationships |
| **GitHub** | Version control, issues (including page feedback), and releases |

Terminology work in this project follows the spirit of ISO 704 (concept analysis, relationships, definitions, designations) and uses UML-style concept diagrams consistent with ISO 24156-1 for illustrating relationships.

## How the vocabulary is organized

This repository holds a **single vocabulary namespace** split into modular Turtle files:

1. **`itsVocabulary.ttl`** — master ontology: site title, license, versioning, and imports of all top-level groups.
2. **`core.ttl`** — shared annotation and object/datatype properties used across modules.
3. **`*-group.ttl`** — thematic collections (for example Vehicle Terms) that import related patterns.
4. **`*-pattern.ttl`** — coherent sets of related terms (for example Vehicle Component Terms) that declare the OWL classes.

All modules share the namespace `https://w3id.org/itsdata/vocab/` (preferred prefix `itsVocab`). Local IRIs use lowerCamelCase (for example `:roadVehicle`); display names come from `skos:prefLabel` (for example `"road vehicle"`).

This modular layout lets editors focus on one pattern at a time while the generation scripts assemble a unified site under Home → group → pattern → term.

## Where to start

1. Read [naming conventions](naming-conventions.md) before adding files or concepts.
2. Follow [ontology formats](ontology-formats.md) for required annotations and clause numbering.
3. Author content in Turtle as described in [turtle.md](turtle.md).
4. Run the generators documented in [python/README.md](../python/README.md) and review the site locally with MkDocs.
5. Use **Comment on this page** on the published site (or open a GitHub issue with the page-feedback template) to propose corrections.
