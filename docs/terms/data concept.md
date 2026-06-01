[Home](../index.md) · [Core Terms](groups/Core Terms.md) · [Data Concept Management Terms](patterns/Data Concept Management Terms.md) · data concept

# data concept

[data element](data element.md), [class](class.md), [value domain](value domain.md), [data frame](data frame.md), [message](message.md) or [interface dialogue](interface dialogue.md) defined, at a minimum, with an unambiguous identifier and a definition

<object type="image/svg+xml" data="../../diagrams/data concept.dot.svg">
    <img alt="data concept Diagram" src="../../diagrams/data concept.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.1.10.1

Note 1 to entry: In order to exchange a value corresponding to a data concept, more information than an identifier, a name and a definition can be needed. For a property, a data type is needed. Depending on the kind of property, other data elements such as unit of measure, and language, can be needed as well. The additional information can be given in the [data dictionary](data dictionary.md), in a data specification that references the data concept or associated with the data themselves.

History note: Introduced in ISO/TS 14812:2022

## Specializations of data concept

| Class | Description |
| --- | --- |
| [class](class.md) | set of ideas, abstractions or things in the real world that are identified with explicit boundaries and meaning and whose properties and behaviour follow the same rules |
| [data element](data element.md) | unit of data that is considered in a given context to be indivisible and which includes an unambiguous representational form |
| [data frame](data frame.md) | specific grouping of [data elements](data element.md) that describes information of interest through a useful grouping of more atomic properties about one or more [classes](class.md) |
| [interface dialogue](interface dialogue.md) | bi-directional communication sequence between two parties in accordance with predetermined protocols |
| [message](message.md) | grouping of [data elements](data element.md), [data frames](data frame.md), or data elements and data frames that is used to convey information |
| [value domain](value domain.md) | a set of permissible values |

## Relationships for data concept

| Property | Constraint |
| --- | --- |
| describes | some entity |
| storedIn | some dataDictionary |

