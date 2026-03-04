# UI/UX Feedback

**ID:** Feedback-20260226-232440
**URL:** http://127.0.0.1:5858/
**Date:** 2026-02-26 23:47:33

## Selected Elements

- `{'selector': 'select:nth-child(2)', 'parents': ['div.modal-container', 'div.modal-body', 'div.action-context-section', 'div.context-ref-group']}`

## Feedback

let's do several fix or CR change. 1. by default the context input should choose the file from prior action deliverables not auto-detect. if no deliverable choose auto-detect. 2. we no longer need to use the placeholder in copilot-prompt.json if in workflow mode, instead, we should use for example $output:raw-idea or $output-folder:ideas-folder in the prompt, so when we choose any file in the context, we should able to preview them in the instructions text box.

since for non-workflow mode, we still need use a different way to deal with prompt. why not in the copilot-prompt, let's add a field called, "workflow-prompts": {...}, for example:  "workflow-prompts": [
      {
        "id": "refine-idea",
        "icon": "bi-stars",
        "input_source": [
          "compose_idea"
        ],
        "prompt-details": [
          {
            "language": "en",
            "label": "Refine Idea",
            "command": "refine the idea <$output:raw-idea$> <and uiux reference: $uiux-reference$> with ideation skill"
          },
          {
            "language": "zh",
            "label": "完善创意",
            "command": "使用创意技能, 完善创意 <$output:raw-idea>"
          }
        ]
      }
placeholder logic for workflow-prompts: <and uiux reference: $uiux-reference$>
1. there are two type of data with in <>, a. is string literal, "and uiux reference: ", b. $uiux-reference$ which should be replaced by related context input.
2. if the related context value is N/A, then any string literal within <> should not be parsed.

Migrate all workflow-mode prompts into workflow-prompts.

## Screenshot

![Screenshot](x-ipe-docs/uiux-feedback/Feedback-20260226-232440/page-screenshot.png)
