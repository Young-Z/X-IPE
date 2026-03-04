I would like to update existing auto_proceed and require_human_review behavior to workflow skills and all task based skills.

1. let's introduce a general structure to all task-based skills, and merge auto_proceed and require_human_review into one. 

process_preference:
  auto_proceed: 'manual | auto | stop_for_question'

a. by default is manual, which between each task stop and wait user instruction, or any questions within a single skill execution stop for user feedback.
b. auto: no any user instruction required, x-ipe ai agent base on the defined workflow to do it automatically, if any conflict happens, have an decision_making_skill to resolve or answer the questions. for the skill detail I will define below.
c. stop_for_question, between task, still wait for user instruction to continue, but within skill execution any question or conflicts, call decision_making_skill to get answer or resolve conflict.

make sure skill creator set this input parameter as skill basic input so it may need update the skill.

2. decision_making_skill
a. it has an input called decision_context which require the calling skill to pass to it.
b. step for the skill to process
- step1: identify the promble type base on the context, listing promblem in the context, classify the promblem to questions or conflicts
- step2: study the project docs, tests or coding to try to find answers to these questions.
- step3: if cannot really answer by the insight from project, search web to try to find answers, if no then leave a notes.
- step4: have a subagent critique but give constructive feedback base on the problem related principles
- step5: refine the answer/solutions to the question or conflicts.
- step6: record these questions/conflicts and answers/solutions as a decision table into decision_making.md under x-ipe-docs/decision_made_by_ai.md for later reference, decision_made_by_ai.md needs a template in the skill

3. update all the existing task-based skills using skill-creator skill
a. update the input parameter and input initlization section to support process_preference.auto_proceed
b. update the output parameter of each skill to support process_preference.auto_proceed
c. update each skill remove human review section, only keep human feedback for question, conflect resolving related decision making.
d. update each skill, for places require human decision making, base on the input value process_preference.auto_proceed to see if interupt for human feedback or call skill decision_making_skill to get the feedback.

4. update workflow skill 
a. if process_preference.auto_proceed is auto or stop_for_question, auto invoke any following tasks base on next step 'next suggested steps' from task based skill. if there are many steps suggested, call decision_making_skill to choose one and execute.
b. clean up any other execution stopping logic, beside process_preference.auto_proceed condition to decide stop to auto proceed no other logic should control flow behavior.

5. workflow mode to support auto_proceed, at feature level panel, we should have a switch for flow proceed for all feature level actions: manual | auto | stop_for_question
a. user can change it anytime, it should update the workflow-{name}.json to change the value(workflow-template.json should have a the attribute template and default value).
b. update all the task based skills, if it's in workflow mode, they should check workflow-{name}.json to get the value of process_preference.auto_proceed



