# Ontology Serialization

## Expressing the vocabulary in Turtle

**Turtle (Terse RDF Triple Language, `.ttl`)** is the authoritative format for the ISO 14812 ontology in this repository. All editorial changes to terms, groups, and patterns are made in Turtle under `docs/`; Markdown and diagrams are generated from those files.

### What is Turtle?

Turtle is a compact, text-based syntax for RDF graphs (subject–predicate–object triples). It is a W3C standard and is widely supported by ontology editors, RDF libraries (including RDFLib), and Git-friendly workflows.

Minimal example of the style used in this project:

```turtle
BASE <https://w3id.org/itsdata/vocab/>
PREFIX : <https://w3id.org/itsdata/vocab/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

:travellerTerms a owl:Ontology ;
    dcterms:title "Traveller Terms"@en ;
    dcterms:modified "2026-05-29"^^xsd:date ;
    owl:imports <core.ttl> .

:pedestrian a owl:Class ;
    rdfs:subClassOf :traveller ;
    skos:definition "[person](person.md) who is travelling on foot"@en ;
    skos:historyNote "Introduced in ISO/TS 14812:2022"@en ;
    skos:prefLabel "pedestrian"@en ;
    :clause "3.6.1.4"@en .
```

### Why Turtle is preferred here

- **Readable diffs** — reviews and Git history stay understandable.
- **Compact** — less boilerplate than RDF/XML for large vocabularies.
- **Tooling** — RDFLib, Protégé export, and this project’s generators all consume Turtle well.
- **Alignment with SPARQL** — similar abbreviation patterns help when querying the graph.
- **Community practice** — many ITS and Linked Data vocabularies are published as Turtle.

### Comparison to other formats

| Format | Role relative to this project |
|--------|-------------------------------|
| **RDF/XML** | Valid exchange syntax; not the editorial source here |
| **Manchester / Functional / OWL/XML** | Useful in editors; not used as the repository source |
| **JSON-LD** | Fine for web APIs; not the MkDocs generation input |

OWL has an abstract structural specification independent of syntax. This project standardizes on Turtle as the stored form.

## File roles in Turtle

| File | Contents |
|------|----------|
| `itsVocabulary.ttl` | Master ontology metadata and imports of groups |
| `core.ttl` | Shared `owl:AnnotationProperty`, object properties, datatype properties |
| `*-group.ttl` | Group ontology + `owl:imports` of patterns |
| `*-pattern.ttl` | Pattern ontology + term classes (and any pattern-local properties) |

See [naming-conventions.md](naming-conventions.md) for how these names drive automation.

## Expressing relationships

Typical OWL constructs used on terms:

```turtle
:motorVehicle a owl:Class ;
    rdfs:subClassOf :motorizedVehicle ,
        :roadVehicle ;
    skos:prefLabel "motor vehicle"@en ;
    :clause "3.7.6.3"@en .
```

Restrictions (anonymous class expressions) appear where needed:

```turtle
:someClass a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ;
            owl:onProperty :startsAt ;
            owl:someValuesFrom :someOtherClass ] .
```

Keep axiomatization accurate but proportionate: this vocabulary prioritizes clear definitions and navigable hierarchies for standards users, not heavyweight reasoning suites.

## Constraining data with SHACL (guidance)

Best practice in Semantic Web engineering is to separate:

- **OWL** — open-world semantics: what concepts *are* and how they relate;
- **SHACL** — closed-world validation: cardinality, datatypes, and quality rules for instance data.

ISO 14812 in this repository is primarily a **definitional vocabulary**. Instance-data validation with SHACL is optional and not currently required for website generation.

If SHACL is added later:

1. Keep shapes in separate files (recommended suffix `*-shacl.ttl`).
2. Target vocabulary classes with `sh:targetClass`.
3. Do not overload OWL with application-specific “exactly one” rules that belong in shapes.
4. Document shapes with `rdfs:label` and clear `sh:message` text.

Example pattern (illustrative only):

```turtle
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX : <https://w3id.org/itsdata/vocab/>

:RoadVehicleShape a sh:NodeShape ;
    sh:targetClass :roadVehicle ;
    sh:property [
        sh:path :clause ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Every published term should have a clause number."
    ] .
```

## Authoring tips for this repository

1. Copy an existing pattern file as a template when adding a new coherent set of terms.
2. Assign `:clause` values that continue the parent clause sequence without gaps.
3. Use `skos:prefLabel` for the display term; keep the IRI local name in lowerCamelCase.
4. After edits, run `ttl2mkdocs.py` from the repository root and check the run summary for clause warnings.
5. Preview with `mkdocs serve` before opening a pull request.
