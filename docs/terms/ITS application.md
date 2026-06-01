[Home](../index.md) · [Technology Terms](groups/Technology Terms.md) · [Its Application Terms](patterns/Its Application Terms.md) · ITS application

# ITS application

requirements for an [ITS service](ITS service.md) that involves an association of two or more complementary [ITS-S application processes](ITS-S application process.md)

<object type="image/svg+xml" data="../../diagrams/ITS application.dot.svg">
    <img alt="ITS application Diagram" src="../../diagrams/ITS application.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.2.8.1

Note 1 to entry: An ITS application can also involve associations with nodes that are not ITS stations.

Note 2 to entry: This is a clarification of the ISO 21217:2020 definition that described this as an instantiation.

History note: 2025: Revised to be "requirements for" rather than "realization of" to clarify that it is a design-level artifact that is assigned an identifier (i.e., ITS-AID) rather than an implementation. Added Notes to entry.

History note: Introduced in ISO/TS 14812:2022

## Relationships for ITS application

| Property | Constraint |
| --- | --- |
| involves | min 2 owl::Thing |
| realizationOf | some itsService |

