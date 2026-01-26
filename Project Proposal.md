# Project Proposal

I would like to create a lightweight project management web application which can be used to review the project created by AI agent.

## Background and Rationale
- For AI agent and Human collaboration usually text based document is preferred for easy management by both parties.
- For AI agent created project, since the most of the work is done by AI agent, so text based document is more suitable for AI agent to update the project status.
- So for AI agent we already have text based project management documents like project task board, feature trackers, requirement specifications etc.

However, for Human user, text based document with native os file viewer/editor is not very user friendly.

So we would like to create a lightweight web application to provide better user experience for human user to view and manage the project created by AI agent.

## Sample AI Created Project Structure
```
Sample Project Root
├── playground
|   ├── README.md
│   ├── playground_app.py
│   └── tests
│       └── test_playground_app.py
├── docs
│   ├── planning
│   │   └── task-board.md
│   │   └── features.md
│   └── requirements
│       ├── FEATURE-001
│       │   ├── specification.md
│       │   └── technical-design.md
│       ├── FEATURE-002
│       │   ├── specification.md
│       │   └── technical-design.md
│       └── FEATURE-003
│           ├── specification.md
│           └── technical-design.md
├── tests
│   ├── test_feature_001.py
│   ├── test_feature_002.py
│   └── test_feature_003.py
└── src
    ├── feature_001.py
    ├── feature_002.py
    └── feature_003.py
```

## Proposed UIUX and Features

### Web Application Layout
- It's life and right layout, life side bar for navigation and right side for content display.
- Its bottom has a pop-up console can be toggled to show an interactive terminal for Human to interact.
- The sidebar contains menu for project plan, requirements/technical design and code repository.

#### Left Sidebar Menu
- The content should be dynamically loaded based on the project structure created by AI agent.
- When new feature is added, the web application should be able to automatically detect and display the new feature without manual intervention.
- The top level menu should have three defined entries:
    - Project Plan: should mapping to `x-ipe-docs/planning/` folder
    - Requirements/Technical Design: should mapping to `x-ipe-docs/requirements/` folder
    - 
    - Code Repository: should mapping to `src/` folder
- Each top level menu can be expanded to show the sub folder and files under the folder.

#### Right Content Display
- The content area should be based on the file extension to provide proper rendering.
    > For markdown file, it should be rendered as HTML with proper styling
    > For diagram in markdown file, if it's mermaid syntax, it should be rendered as mermaid diagram
    > For code file, it should be have code viewer with syntax highlighting
- The content area should have a edit button to switch to edit mode for human user to edit the content.
- When content is updated by AI agent on file system, the web application should be able to detect the change and update the content area automatically.

#### Bottom Pop-up Console
- By default the console is collapsed to be a thin bar to save space.
- When expanded, it should provide an interactive terminal to call with server side to run python commands.

### UIUX Design Language
- Use modern responsive design language like Bootstrap 5.
- The UIUX should be fancy.

### Technology Stack
- Backend: Python with Flask framework
- Frontend: HTML/CSS with Bootstrap 5 and JavaScript
- Database: SQLite for any persistence if needed
- For Markdown, Code(HTML, JS, CSS, PYTHON etc common code types), interactive terminal rendering, you can do research on existing open source libraries to integrate.

### Some of Technical Design Thinking
1. This web application usually under the same project root created by AI agent, so it can directly read the project files from file system. But for flexibility, we can also provide configuration to specify the project root path.