[Home](../index.md) · [Infrastructure Terms](groups/Infrastructure Terms.md) · [Road Network Terms](patterns/Road Network Terms.md) · road model

# road model

representation of a [road network](road network.md)

<object type="image/svg+xml" data="../../diagrams/road model.dot.svg">
    <img alt="road model Diagram" src="../../diagrams/road model.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.3.5.3

Note 1 to entry: Road models for different [systems](system.md) will often define different models. For example, a public [transport system](transport system.md) can define [road links](road link.md) based on the [spatial location](spatial location.md) of bus stops while a traffic system can define road links based on the spatial location of [junctions](junction.md).

History note: Introduced in ISO/TS 14812:2022

## Relationships for road model

| Property | Constraint |
| --- | --- |
| constitutes | some link |
| constitutes | some node |
| represents | some roadNetwork |

