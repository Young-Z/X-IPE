# Idea Summary: MyClientService AI Agent

> **IDEA-015** | Version: 1.1 | Date: 2026-01-27

## Executive Summary

Build an AI-powered chat assistant integrated into "My Client Service" application. The AI agent will enable internal staff to complete complex multi-step workflows through natural language conversation, with full automation capability via MCP (Model Context Protocol) tool integration.

## Problem Statement

- Current application has complex functions requiring many steps across multiple pages
- Internal staff spend significant time navigating through workflows
- Training new staff on complex procedures is time-consuming
- Human errors in multi-step processes

## Solution Overview

A conversational AI assistant that:
1. Understands user intent in natural language
2. Maps requests to appropriate business functions
3. Executes operations automatically via MCP tools
4. Provides feedback and confirmation to users

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary Users | Internal staff (employees, support agents) | Controlled environment, trusted users |
| AI Behavior | Full Automation | Execute tasks directly on user's behalf |
| Frontend Stack | HTML5 + Vanilla JS | Matches existing application |
| Backend/MCP Stack | Python (FastAPI + FastMCP) | Best LLM libraries, quick development |
| LLM Provider | OpenAI Compatible (DashScope) | Flexibility, cost-effective |
| UI Integration | Floating chat widget (bottom-right) | Non-intrusive, always accessible |
| Widget Rendering | Simple type + data | AI returns widget type, frontend renders |
| Widget Style | Modern/Friendly | Rounded corners, soft colors, approachable |
| Security | Basic logging | Minimal compliance requirements |

## Architecture Overview

```architecture-dsl
# MyClientService AI Agent - System Architecture

## Module View

@layer Presentation
  - Chat Widget | Floating UI component | vanilla-js
  - Message Renderer | Display AI responses | html-css
  - Widget Library | Rich UI components | vanilla-js

@layer Application
  - AI Agent Service | LLM orchestration | python
  - Conversation Manager | Session & context | python
  - MCP Client | Tool execution | fastmcp

@layer Integration
  - MCP Server | Tool definitions | fastmcp
  - REST API Adapter | Existing API calls | python
  - Business Rules Engine | Domain logic | python

@layer Data
  - Conversation Store | Chat history | db
  - Session Cache | Context memory | redis
  - Audit Log | Action tracking | db
```

## System Landscape

```architecture-dsl
# System Landscape

## Landscape View

@zone Client Browser
  @app Chat Widget | Web Component | #4A90D9

@zone AI Backend
  @app AI Agent | Orchestrator | #6C5CE7
  @app MCP Server | Tool Provider | #00B894

@zone Existing System
  @app My Client Service | Main App | #FDCB6E
  @db Client Database | Data Store | #E17055

@flow
  Chat Widget --> AI Agent : user message
  AI Agent --> MCP Server : tool calls
  MCP Server --> My Client Service : REST API
  My Client Service --> Client Database : CRUD
  MCP Server --> AI Agent : tool results
  AI Agent --> Chat Widget : response
```

## Component Details

### 1. Chat Widget (Frontend)

```infographic
list-grid-badge-card
data
  title Chat Widget Features
  lists
    - label Message Input
      desc Text box with send button
      icon keyboard
    - label Message History
      desc Scrollable conversation view
      icon comment multiple
    - label Typing Indicator
      desc Show when AI is processing
      icon dots horizontal
    - label Minimize/Expand
      desc Toggle widget visibility
      icon arrow expand
    - label Quick Actions
      desc Suggested prompts
      icon lightning bolt
    - label Status Badge
      desc Connection & AI status
      icon circle
theme
  palette #3b82f6 #10b981 #f59e0b
```

### 2. Rich Widget Library

The chat supports predefined rich widgets for structured AI responses. AI returns widget type + data, frontend renders appropriately.

#### Widget Catalog

```infographic
list-grid-candy-card-lite
data
  title Predefined Chat Widgets
  lists
    - label Multi-Choice Buttons
      desc Single or multiple selection options
      icon radiobox marked
    - label Customer Info Card
      desc Display client details with avatar
      icon account card
    - label Order Summary Card
      desc Transaction details with status
      icon cart check
    - label Data Table
      desc Scrollable list of records
      icon table
    - label Form Inputs
      desc Text, date, dropdown fields
      icon form textbox
    - label File Upload
      desc Drag-drop or browse attachments
      icon file upload
    - label Confirmation Dialog
      desc Yes/No action buttons
      icon check circle
    - label Progress Indicator
      desc Status steps or loading bar
      icon progress check
theme
  palette #8B5CF6 #EC4899 #14B8A6 #F59E0B
```

#### Widget Response Format

AI returns structured responses that the frontend interprets:

```json
{
  "type": "widget",
  "widget": "multi-choice",
  "data": {
    "question": "Which client do you want to update?",
    "options": [
      {"id": "1", "label": "John Smith - #C001"},
      {"id": "2", "label": "Jane Doe - #C002"}
    ],
    "multiple": false
  }
}
```

#### Widget Examples

**Multi-Choice Buttons**
```
┌─────────────────────────────────────────┐
│ Which action would you like to perform? │
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Update Info  │  │ View History │    │
│  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ New Order    │  │ Contact      │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

**Customer Info Card**
```
┌─────────────────────────────────────────┐
│  ┌───┐                                  │
│  │ 👤│  John Smith                      │
│  └───┘  Customer #C001                  │
│         ─────────────────────────       │
│  📧 john.smith@email.com                │
│  📱 +1 555-0123                         │
│  📍 New York, NY                        │
│         ─────────────────────────       │
│  Status: ● Active    Since: 2024-01    │
│                                         │
│  [View Profile]  [Edit]  [Contact]      │
└─────────────────────────────────────────┘
```

**Order Summary Card**
```
┌─────────────────────────────────────────┐
│  Order #ORD-2026-0142     🟢 Confirmed  │
│  ─────────────────────────────────────  │
│  Customer: John Smith                   │
│  Date: 2026-01-27                       │
│  ─────────────────────────────────────  │
│  Items:                                 │
│    • Product A × 2         $199.00      │
│    • Service B × 1         $50.00       │
│  ─────────────────────────────────────  │
│  Total:                    $249.00      │
│                                         │
│  [View Details]  [Track]  [Invoice]     │
└─────────────────────────────────────────┘
```

**Data Table**
```
┌─────────────────────────────────────────┐
│  Recent Clients (5 of 23)               │
│  ─────────────────────────────────────  │
│  Name          │ Status  │ Last Active  │
│  ─────────────────────────────────────  │
│  John Smith    │ Active  │ Today        │
│  Jane Doe      │ Active  │ Yesterday    │
│  Bob Wilson    │ Pending │ 3 days ago   │
│  ─────────────────────────────────────  │
│            [Load More]                  │
└─────────────────────────────────────────┘
```

**Confirmation Dialog**
```
┌─────────────────────────────────────────┐
│  ⚠️ Confirm Action                      │
│                                         │
│  Are you sure you want to update the    │
│  client status to "Inactive"?           │
│                                         │
│  This will affect 3 pending orders.     │
│                                         │
│     [Cancel]          [Confirm]         │
└─────────────────────────────────────────┘
```

**Form Input**
```
┌─────────────────────────────────────────┐
│  Update Client Information              │
│  ─────────────────────────────────────  │
│  Email:                                 │
│  ┌─────────────────────────────────┐   │
│  │ john.smith@email.com            │   │
│  └─────────────────────────────────┘   │
│  Phone:                                 │
│  ┌─────────────────────────────────┐   │
│  │ +1 555-0123                     │   │
│  └─────────────────────────────────┘   │
│  Status:                                │
│  ┌─────────────────────────────────┐   │
│  │ Active                        ▼ │   │
│  └─────────────────────────────────┘   │
│                                         │
│     [Cancel]          [Submit]          │
└─────────────────────────────────────────┘
```

**Progress Indicator**
```
┌─────────────────────────────────────────┐
│  Order Processing                       │
│  ─────────────────────────────────────  │
│  ✓ Received  →  ✓ Validated  →  ● Processing  →  ○ Complete
│                                         │
│  Current: Verifying inventory...        │
└─────────────────────────────────────────┘
```

### 3. AI Agent Service (Backend)

```infographic
sequence-snake-steps-compact-card
data
  title AI Agent Processing Flow
  sequences
    - label Receive Message
      desc User input arrives
      icon message
    - label Parse Intent
      desc LLM understands request
      icon brain
    - label Plan Actions
      desc Determine tool sequence
      icon sitemap
    - label Execute Tools
      desc Call MCP tools
      icon cog
    - label Generate Response
      desc Format result for user
      icon comment check
    - label Send Reply
      desc Return to chat widget
      icon send
theme
  palette #6C5CE7 #A29BFE #DDD6FE
```

### 3. MCP Server (Tool Layer)

```infographic
list-column-vertical-icon-arrow
data
  title MCP Tool Categories
  lists
    - label Client Management
      desc Create, update, search clients
      icon account multiple
    - label Order Processing
      desc Place orders, check status
      icon cart
    - label Document Handling
      desc Generate, upload, retrieve docs
      icon file document
    - label Reporting
      desc Run reports, export data
      icon chart bar
    - label Workflow Actions
      desc Trigger business processes
      icon sitemap
theme
  palette #00B894 #55EFC4 #81ECEC
```

## Tech Stack

```infographic
list-grid-ribbon-card
data
  title Technology Stack
  lists
    - label Frontend
      desc HTML5, Vanilla JS, CSS3
      icon web
    - label AI Backend
      desc Python 3.11+, FastAPI
      icon language python
    - label LLM Integration
      desc OpenAI SDK, DashScope
      icon brain
    - label MCP Framework
      desc FastMCP (Python)
      icon puzzle
    - label Caching
      desc Redis (sessions)
      icon database
    - label Logging
      desc Structured JSON logs
      icon text box
theme
  palette #2D3436 #636E72 #B2BEC3
```

## Implementation Phases

```infographic
sequence-roadmap-vertical-simple
data
  title Implementation Roadmap
  sequences
    - label Phase 1: Foundation
      desc MCP Server + Basic Tools (2 weeks)
      icon foundation
    - label Phase 2: AI Agent
      desc LLM integration + Orchestration (2 weeks)
      icon robot
    - label Phase 3: Chat UI
      desc Widget development + Integration (1 week)
      icon chat
    - label Phase 4: Tool Expansion
      desc Add more MCP tools (ongoing)
      icon puzzle
    - label Phase 5: Optimization
      desc Performance + UX refinement (1 week)
      icon speedometer
theme
  palette #0984E3 #74B9FF #A8D8FF
```

## Key Risks & Mitigations

```infographic
compare-binary-horizontal-simple-fold
data
  title Risks vs Mitigations
  compares
    - label Risks
      children
        - label LLM Hallucination
          desc AI may misunderstand or fabricate
        - label API Rate Limits
          desc DashScope throttling
        - label Security Gaps
          desc Unauthorized operations
        - label User Adoption
          desc Staff may resist change
    - label Mitigations
      children
        - label Confirmation prompts for critical actions
          desc Add verification step
        - label Request queuing + caching
          desc Handle rate limits gracefully
        - label Role-based tool access
          desc Limit tools per user role
        - label Training + gradual rollout
          desc Onboard in phases
theme
  palette #E74C3C #27AE60
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Task Completion Rate | >90% | Successful AI-executed tasks |
| Average Task Time | -50% | Before/after comparison |
| User Adoption | >70% | Staff using chat weekly |
| Error Reduction | -60% | Fewer manual errors |

## Next Steps

1. **Mockup** - Create chat widget UI mockup
2. **Architecture** - Detail component interactions
3. **MCP Design** - Define initial tool set
4. **Prototype** - Build MVP with 3-5 core tools

---

*Refined by: Ember | Task: TASK-186*
