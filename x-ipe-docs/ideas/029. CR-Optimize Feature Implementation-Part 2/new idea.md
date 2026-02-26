since for the implementation, as we mentioned in the idea, it should accept multi input files for difrerent prior
  actions, looks like it's not here. for example the section title in the modal window should be call input files,
  the sub title for the first input should be feature specification, and then the dropdown should have two option, 1
  is the specification.md from prior action, option 2. should be called auto-detect. the second subtitle is technical
  design, and dropdown design should be similar to the first one. 
**important** let's rename input files to action context
for the action context we should able to auto detect them via workflow-template.json, so let's change the workflow-template.json to support the rules a bit.
"compose_idea": {
          "optional": false,
					// change the name from deliverable_category to deliverable, and let's use special syntax to identify or tagging deliverables, for now let's have output file and output folder two reference. Skills should base on these to input extra context, see Skill update section for details.
          "deliverables": ["$output:raw-idea", "$output-folder:ideas-folder"], 
          "next_actions_suggested": ["refine_idea", "reference_uiux"]
        },
        "reference_uiux": {
          "optional": true,
          "deliverables":  ["$output:uiux-reference"],
          "next_actions_suggested": ["design_mockup", "refine_idea"]
        },
        "refine_idea": {
          "optional": false,
					"action_context": {
					   "raw-idea": { required: true, candidates: ideas-folder},
						 "uiux-reference": { required: false},
						 // it can add more context reference to the predefined outputs from deliverable_outputs from prior actions
					},
          "deliverables": ["$output:refined-idea", "$output-folder:refined-ideas-folder"], 
          "next_actions_suggested": ["design_mockup", "requirement_gathering"]
        }
				
for action modal window, let's update as below:
the uiux for input files types should be base on context in workflow-template.json
				
for workflow file in the x-ipe-docs/engineering-workflow, let's update deliverables structure a bit, it should match the deliverable output defined in the workflow template
    "ideation": {
      "status": "in_progress",
      "actions": {
        "compose_idea": {
          "status": "done",
          "deliverables": {
            raw-idea: "x-ipe-docs/ideas/wf-001-greedy-snake/new idea.md",
            ideas-folder: "x-ipe-docs/ideas/wf-001-greedy-snake"
          },
          "next_actions_suggested": [
            "refine_idea",
            "reference_uiux"
          ]
        },
        "reference_uiux": {
          "status": "pending",
          "deliverables": [],
          "optional": true
        },
        "refine_idea": {
          "status": "done",
					//add attribute, and Context section in the modal window, should base on this to display
					//the selected vaule of the dropdown list in the modal window should be shown here.
					"context": {
					raw-idea: "x-ipe-docs/ideas/wf-001-greedy-snake/new idea.md",
					uiux-reference: N/A
					}
					//update deliverables
          "deliverables": {
            refined-idea: "x-ipe-docs/ideas/wf-001-greedy-snake/refined-idea/idea-summary-v2.md",
						refined-idea-folder: "x-ipe-docs/ideas/wf-001-greedy-snake/refined-idea"
          },
          "next_actions_suggested": [
            "design_mockup",
            "requirement_gathering"
          ]
        },
Action related Skills update
1. related skills, 
	workflow:
    name: "N/A"  # workflow name, default: N/A
    action: "refine_idea" 
		<  # Dynamic context reference for workflow mode by reading the workflow-{workflow name}.json>
		extra_context_reference: N/A