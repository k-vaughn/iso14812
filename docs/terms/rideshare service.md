[Home](../index.md) · [Service Terms](groups/Service Terms.md) · [Shared Transport Service Terms](patterns/Shared Transport Service Terms.md) · rideshare service

# rideshare service

[cooperative](cooperative.md) [shared transport service](shared transport service.md) that transports [passengers](passenger.md) [concurrently](concurrent.md)

<object type="image/svg+xml" data="../../diagrams/rideshare service.dot.svg">
    <img alt="rideshare service Diagram" src="../../diagrams/rideshare service.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.5.11.4

History note: Introduced in ISO/TS 14812:2022

## Relationships for rideshare service

| Property | Constraint |
| --- | --- |
| attrFinancialModel | has cooperative |
| attrOperationalModel | has concurrent |
| attrTransportItem | has passengers |
| subClassOf | sharedTransportService |

