[Home](../index.md) · [Infrastructure Terms](groups/Infrastructure Terms.md) · [Road Network Terms](patterns/Road Network Terms.md) · lane link

# lane link

[link](link.md) that represents a [lane](lane.md) of a [road link](road link.md)

<object type="image/svg+xml" data="../../diagrams/lane link.dot.svg">
    <img alt="lane link Diagram" src="../../diagrams/lane link.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.3.5.9

Note 1 to entry: A [lane segment](lane segment.md) can start or end at [spatial locations](spatial location.md) other than the start or end of the corresponding [road segment](road segment.md) (e.g. a lane can start mid-block).

Note 2 to entry: A lane segment only includes the sequential lane links, it does not include lane links from adjacent lanes.

History note: Introduced in ISO/TS 14812:2022

## Relationships for lane link

| Property | Constraint |
| --- | --- |
| constitutes | some laneSegment |
| subClassOf | link |

