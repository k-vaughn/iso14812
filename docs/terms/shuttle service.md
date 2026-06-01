[Home](../index.md) · [Service Terms](groups/Service Terms.md) · [Shared Transport Service Terms](patterns/Shared Transport Service Terms.md) · shuttle service

# shuttle service

[shared transport service](shared transport service.md) that transports [passengers](passenger.md) between two specified [spatial locations](spatial location.md)

<object type="image/svg+xml" data="../../diagrams/shuttle service.dot.svg">
    <img alt="shuttle service Diagram" src="../../diagrams/shuttle service.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.5.11.1

Note 1 to entry: Each location can be defined as point, linear or area locations. However, the areas of the two locations should not overlap.

History note: Introduced in ISO/TS 14812:2022

## Relationships for shuttle service

| Property | Constraint |
| --- | --- |
| attrTransportItem | has passengers |
| subClassOf | sharedTransportService |

