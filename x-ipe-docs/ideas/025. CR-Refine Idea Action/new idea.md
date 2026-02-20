when user click on the refine idea action button in workflow.

it should open a modal window

in the modal window it should show following content.

1. show a refine instruction text area the default instructions of refinement from copilot-prompt.json(it's readonly)
2. below the efine instruction text box, show a text area show a text box for extra instructions, if anything, your can type here
3. there should be a "copilot" button at bottom of the modal window. when clicks it. do following steps:
  > open console window
  > find a avaible session(not in execution, in normal cmd not in any cli, and can accept commands), then switch the session, if no avaible session, create a new session
  > rename the session name to wf-{name}-refine-idea
  > type agent cli with the instructions, if extra instruction defined by user, using syntax --extra-instructions detailed instruction within the instruction block: agent-cli-command "{instructions}"

in idea refinement (after user hit enter to in the console session with typed agent cli, with current setting, agent will automatically call refinement skill)
update the refinement skill a bit
1. it should able to accept extra input as a input parameter.
2. you can define where to execute the extra instruction when you update the skill
3. now the refined idea should be under the selected idea folder/refined-idea/
4. now the refined idea need to call workflow-manager via agent-app-interaction mcp with the path of the refined idea path in DoD(the data should extract from output data model to keep consistency and simple)
6. when refinment skill done it's work, it need to output the file path it's generated and the status of workflow manager execution response. (the default status is pending)

update the execution skill a bit, in it's dod also check if the status is pending if it's pending which means the skill haven't call the workflow manager to update the status.

workflow manager and agent-app-interaction mcp
1. they should provide workflow status update api, with the action, it's status and the next task to act as input(the data should extract from output data model to keep consistency and simple), then workflow manager update the status to the wf-{xxx}.json, if success, give success response, if error, provide error response.

after refinement done by ai agent via agent cli:
1. the action status and the deliverable should be updated and the next action should be indicated.
2. show the refined-idea folder in deliverable
3. when click on the folder, it should open the modal window and let's reuse the linked idea file viewer and preview, so we can select the idea file in the refine-idea folder and view them