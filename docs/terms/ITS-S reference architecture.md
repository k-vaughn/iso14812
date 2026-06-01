[Home](../index.md) · [Core Terms](groups/Core Terms.md) · [Architecture Type Terms](patterns/Architecture Type Terms.md) · ITS-S reference architecture

# ITS-S reference architecture

[reference architecture](reference architecture.md) for handling communications within a [physical object](physical object.md) as defined in ISO 21217

<object type="image/svg+xml" data="../../diagrams/ITS-S reference architecture.dot.svg">
    <img alt="ITS-S reference architecture Diagram" src="../../diagrams/ITS-S reference architecture.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.1.9.4

Note 1 to entry: The ITS-S reference architecture provides a model for describing communication.

History note: Introduced in ISO/TS 14812:2022

## Relationships for ITS-S reference architecture

| Property | Constraint |
| --- | --- |
| aggregates | some securityEntity |
| aggregates | some facilitiesLayer |
| aggregates | some applicationEntity |
| aggregates | some managementEntity |
| aggregates | some transnetLayer |
| aggregates | some its-sAccessLayer |
| subClassOf | referenceArchitecture |

