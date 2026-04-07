---
title: "Manage Feature Dependencies"
section: "05-common-workflows"
extraction_round: 2
---

# Manage Feature Dependencies

## Overview
Features created during Feature Breakdown can have dependencies on each other. Dependencies control the execution order of feature lane steps.

## Dependency Visualization

### Badge Types
| Badge | Meaning |
|-------|---------|
| ⇉ **Parallel** | No dependencies — can run immediately |
| ⛓ **needs FEATURE-XXX** | Must wait for named feature(s) |
| ⛓ **needs FEATURE-XXX, FEATURE-YYY** | Multiple dependencies |

### SVG Dependency Arrows
1. Click the **"⑆ Dependencies"** button on the workflow card
2. SVG arrows are drawn between dependent feature lanes
3. Arrows show the direction: prerequisite → dependent feature
4. Arrows redraw on window resize

## How Dependencies Affect Execution

1. A feature with ⛓ dependencies **cannot advance a step** until the dependency feature has completed the **same step**
2. Example: FEATURE-050-B depends on FEATURE-050-A
   - B cannot start "Refinement" until A's "Refinement" is done
   - B cannot start "Tech Design" until A's "Tech Design" is done
3. Features with ⇉ Parallel can execute any step immediately

## When Dependencies Are Created
- Dependencies are established during the **Feature Breakdown** action in the Requirement stage
- The AI analyzes feature descriptions and determines which features logically depend on others
- Dependencies are stored in the workflow state JSON under each feature's `depends_on[]` array

## Limitations
- Dependencies cannot be edited in the UI after creation
- To modify dependencies, you would need to use the CLI or edit the workflow state file directly
