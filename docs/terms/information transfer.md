[Home](../index.md) · [Core Terms](groups/Core Terms.md) · [Architecture Physical View Terms](patterns/Architecture Physical View Terms.md) · information transfer

# information transfer

[information flow](information flow.md) from a [physical object](physical object.md) acting as an information provider and sent to another physical object acting as an information consumer

<object type="image/svg+xml" data="../../diagrams/information transfer.dot.svg">
    <img alt="information transfer Diagram" src="../../diagrams/information transfer.dot.png" /> <!-- Fallback for non-SVG browsers -->
</object>

Clause: 3.1.8.5

Admitted term: information flow triple

Note 1 to entry: The term "information flow triple" is used extensively in the Architecture Reference for Cooperative and Intelligent Transportation (ARC-IT; see Reference [25]).

History note: Introduced in ISO/TS 14812:2022

## Relationships for information transfer

| Property | Constraint |
| --- | --- |
| contentsOf | some informationFlow |
| sentFrom | some physicalObject |
| sentTo | some physicalObject |

