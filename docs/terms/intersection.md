[Home](../index.md) · [Infrastructure Terms](groups/Infrastructure Terms.md) · [Junction Terms](patterns/Junction Terms.md) · intersection

# intersection

space where two or more [roads](road.md) meet or cross

<object type="image/svg+xml" data="../../diagrams/intersection.dot.svg">
    <img alt="intersection Diagram" src="../../diagrams/intersection.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.3.6.1

Note 1 to entry: Complex intersections can be viewed as multiple intersections by providing separate designations for distinct [road links](road link.md). For example, one model could depict a complex intersection as being associated with multiple junctions; another model could depict the same physical infrastructure as being multiple intersections that are interconnected by different [roads](road.md), each with its own designator (e.g. "ramp from northbound Road A to eastbound Road B").

Note 2 to entry: Intersections can be associated with zero [junctions](junction.md), such as a motorway crossing a road without any connecting ramps, or can be associated with one or more junctions, such as a diamond [interchange](interchange.md).

History note: Introduced in ISO/TS 14812:2022

## Specializations of intersection

| Class | Description |
| --- | --- |
| [interchange](interchange.md) | [junction](junction.md) with at least one [grade separated manoeuvre](grade separated manoeuvre.md) |
| [junction](junction.md) |  |
| [junction at grade](junction at grade.md) | [junction](junction.md) without any [grade separated manoeuvres](grade separated manoeuvre.md) |

## Relationships for intersection

| Property | Constraint |
| --- | --- |
| meetingOrCrossing | min 2 owl::Thing |

## References to intersection

| Referencing Term | Type of Reference |
| --- | --- |
| [junction](junction.md) | subClassOf |

