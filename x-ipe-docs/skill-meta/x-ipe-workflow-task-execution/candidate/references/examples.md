# Shared lifecycle examples

## Goal-aware adoption example (illustrative, not execution evidence)

An adopting refinement child maps source FR-061-01 to story US-061-A-01 and
GWT AC-061-A-01/02 in its existing specification. A badge is the output;
an operator distinguishing available from unavailable state is the intended
outcome. Planned UI checks are not yet verified engineering delivery, and
stakeholder outcome is not measured. An acceptance child can later verify UI
delivery without asserting operator observation. A changed parent goal invokes
bounded authorized CR replanning and invalidates affected evidence only.
An unmigrated child still needs explicit adoption/ownership reconciliation.

## Lifecycle scenarios

## Direct bug-fix entry with supplied task

Human invokes a task skill with TASK-123 and existing approved context. Child
loads workflow and common lifecycle contract, enters Orient/Plan once. The owner
queries/ensures TASK-123 with exact original role/task_type/description; matching
in_progress returns created=false, preserving timestamps/outputs. The entry
returns readiness to the child, not a recursive dispatch. Child runs domain TDD
and returns task_completion_output. Owner verifies current source/test hashes,
records only authorized status and stops at the configured boundary. Foreign
ownership/context blocks without changes; completed ensure never reruns work.

## Three real decision policies

Human mode: ask a real scope question and wait; after verified work, show outputs
and wait for completion/next-task confirmation. No ceremonial questions for clear
inputs. Full DAO: send bounded message_context to representative, consume
instruction_units and execution_plan, select only an authorized successor after
Verify/Record. Hybrid: actual within-skill questions use bounded DAO guidance;
completion and routing wait for human confirmation, matching the current
DAO Inner-Skill Only UI/specification. Domain-required approval remains human;
a representative's guidance cannot supply missing scope or release authority.
Re-read mode source before routing, including changes from DAO to human.

## Small free-mode change

An approved small change has one linked note with scope/acceptance/design/impact
sections and failing/passing test evidence, not four speculative future tasks.
DoR, TDD and fresh verification still apply. Larger TASK-6749 stays in_progress
when this slice is candidate_ready awaiting review. No app action is marked done
or skipped; no claim that UI mandatory gates already support combined artifacts.

## Workflow implementation action

Resolve app action implementation from workflowStage.ACTION_MAP; required tags
come from workflow-template.json. Tool choice uses implement.code_implementation
in tools.json. Pass the existing workflow.name/action and feature_id. Verify
features[].implement.actions.implementation has done and real keyed impl-files /
impl-folder artifacts after installed writer success. in_progress/skipped/failed,
missing workflow, wrong feature, empty deliverables or stale design/test hashes
block completion. Do not make prerequisite technical_design skipped to unlock it.

## Dirty Git and revision freshness

Existing staged/untracked foreign changes are protected. Wrong configured branch
with dirty work blocks branch switching; no stash, reset, pull or Git commit
default. A user-approved commit is limited to explicit owned paths after index
and diff review; foreign staged changes block it. No implicit push in DAO.
Editing a design, implementation or test after a passing report invalidates the
affected evidence; rerun those checks before completion or authorized routing.

## Candidate review boundary

Structural validation and temporary helper tests support candidate_ready, not
release readiness. Reviewer receives candidate hash, source/test consumer hashes,
exact delta, limitations and deferred child/creator adoption. Review must match
the current revision. No live child, template, app schema, board or Git mutation
is inferred from drafting the common contract.
