for x-ipe-docs/skill-meta/templates/skill-creation-best-practice/skill-general-guidelines.md

beside principle 2, Set Appropriate Degrees of Freedom, we also need an extra principles to define what which scenario use which expression format. for some contents are for human, some contents are for ai agents, so both of their preferred content format for different party.
for example for input and output data model:

- for human we may prefer table view
Task Type Default Attributes
| Attribute | Value |
|-----------|-------|
| Task | Feature Breakdown |
| Category | requirement-stage |
| Next Task Type | Feature Refinement |
| Require Human Review | Yes |

- for agents you may have their prefered way to `view` the data model such as yaml format.

for another example
- for human we may prefer use symbol to highlight
**⚠️ Section order is MANDATORY.** Sections must appear in this exact sequence.

- for agents you may prefer more stright way to express importance.

so i suggest you to base on your understanding for different audiance we should have different expression or content format. And Skill is more for agents or AI to accuratelly learn the functions, the capabilities and the "skills" to work on specific works with the skills learned.