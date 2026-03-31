# 5. Common Workflow Scenarios

## Scenario 1: Building a New Feature from Scratch (End-to-End)

**Goal:** Take a project idea through the complete X-IPE workflow — from initial concept to implemented, tested, and validated features.

**Prerequisites:**
- X-IPE server running at `http://127.0.0.1:5858`
- AI CLI tool connected (Console shows "Connected")
- Project initialized (`x-ipe init` already run)

**Estimated time:** 30-90 minutes (depending on project complexity and AI processing time)

---

### Phase 1: Ideation (Shared)

**Step 1: Create the workflow**
1. Toggle to **WORKFLOW** mode using the header switch
2. Click **"➕ Create Workflow"**
3. In the modal, type: `ecommerce-checkout` (example name)
4. Click **"Create"**
5. **Expected result:** New workflow card appears with "ideation Stage" and "0 features"

**Step 2: Compose your idea**
1. Click **"📝 Compose Idea"** on the workflow card
2. In the text editor that opens, write your idea. Example:
   ```
   Build an e-commerce checkout flow with:
   - Shopping cart management (add, remove, update quantities)
   - Address form with validation
   - Payment integration (Stripe)
   - Order confirmation with email notification
   ```
3. Save the idea
4. **Expected result:** ✓ appears next to "Compose Idea"

**Step 3: (Optional) Reference UI designs**
1. Click **"🎨 Reference UIUX"**
2. A command is dispatched to the AI CLI terminal
3. Wait for the AI to complete (watch terminal output, ~1-3 minutes)
4. **Expected result:** UIUX reference document created in deliverables

**Step 4: Refine the idea with AI**
1. Click **"💡 Refine Idea"**
2. The AI reads your raw idea and produces a polished, structured idea summary
3. Wait for terminal to show completion (~2-5 minutes)
4. **Expected result:** ✓ appears next to "Refine Idea". New deliverable: `idea-summary-v1.md`

---

### Phase 2: Requirement (Shared)

**Step 5: Gather requirements**
1. The Requirement stage unlocks automatically when Ideation mandatory actions are done
2. Click **"📋 Requirement Gathering"**
3. The AI analyzes your refined idea and creates formal requirements
4. Wait for terminal completion (~3-5 minutes)
5. **Expected result:** ✓ appears next to "Requirement Gathering". New deliverable: `requirement-details.md`

**Step 6: Break down into features**
1. Click **"🔀 Feature Breakdown"**
2. The AI analyzes requirements and creates individual features with:
   - Feature IDs (FEATURE-XXX-A, FEATURE-XXX-B, etc.)
   - Feature names and descriptions
   - Dependency chains (which features block others)
3. Wait for terminal completion (~2-5 minutes)
4. **Expected result:** ✓ appears next to "Feature Breakdown". **Feature Lanes** appear showing each feature's progression bar.

Example features created:
```
FEATURE-052-A: Shopping Cart Management          (⇉ Parallel)
FEATURE-052-B: Address Form & Validation         (⇉ Parallel)
FEATURE-052-C: Stripe Payment Integration        (⛓ needs FEATURE-052-A)
FEATURE-052-D: Order Confirmation & Email        (⛓ needs FEATURE-052-C)
```

---

### Phase 3: Implement (Per-Feature)

**Step 7: Refine first feature**
1. In the Feature Lanes section, find **FEATURE-052-A** (or the first parallel feature)
2. Click the **"Refinement"** step in its lane
3. AI creates a detailed specification for this feature
4. Wait for completion (~2-3 minutes)
5. **Expected result:** ✓ appears on "Refinement" step

**Step 8: Technical design**
1. Click the **"Tech Design"** step in the same feature lane
2. AI creates a technical design document with architecture decisions
3. Wait for completion (~2-4 minutes)
4. **Expected result:** ✓ appears on "Tech Design" step. New deliverable: `technical-design.md`

**Step 9: Implement the code**
1. Click the **"Implement"** step
2. AI writes the actual code based on spec and tech design
3. This is typically the longest step (~5-15 minutes)
4. **Expected result:** ✓ appears on "Implement" step. Code files created in project

**Repeat Steps 7-9** for each feature (respecting dependency order).

---

### Phase 4: Validation (Per-Feature)

**Step 10: Run acceptance tests**
1. Click the **"Testing"** step in the feature lane
2. AI generates test cases from the specification and runs them
3. Wait for completion (~3-5 minutes)
4. **Expected result:** ✓ appears on "Testing". New deliverable: `acceptance-test-report.md`

**Step 11: Code refactoring**
1. Click the **"Refactor"** step
2. AI analyzes code quality and refactors if needed
3. Wait for completion (~2-4 minutes)
4. **Expected result:** ✓ appears on "Refactor"

**Step 12: Close the feature**
1. Click the **"Closing"** step
2. AI finalizes the feature (creates PR, updates documentation)
3. **Expected result:** ✓ appears on "Closing"

---

### Phase 5: Feedback (Per-Feature, Optional)

**Step 13: Deploy playground**
1. Click the **"Playground"** step
2. AI deploys an interactive demo for testing
3. **Expected result:** Playground URL or local demo available

**Step 14: Submit change request**
1. Click the **"CR"** step if changes are needed
2. AI documents and tracks the change request

---

## Scenario 2: Changing Interaction Mode Mid-Workflow

**Goal:** Switch from fully manual interaction to DAO-assisted mode for faster execution.

**Prerequisites:** An existing workflow in progress

**Steps:**

1. On your workflow card, find the **"Interaction Mode"** dropdown
2. It currently shows **"👤 Human Direct"**
3. **Click the dropdown** to expand it
4. Three options appear:
   - 👤 Human Direct
   - 🤖 DAO Represents Human
   - 🤖⚡ DAO Inner-Skill Only
5. **Click "🤖 DAO Represents Human"**
6. The dropdown closes and shows the new mode

**What changes:**
- When you click workflow actions, the AI will make routine decisions autonomously
- For important decisions (architecture choices, breaking changes), the AI will still ask you
- Processing is generally faster since fewer approval steps are needed

**When to use:**
- Use **Human Direct** when learning the system or working on critical projects
- Switch to **DAO Represents Human** once you're comfortable with the workflow
- Use **DAO Inner-Skill Only** for maximum automation on well-understood projects

---

## Scenario 3: Managing Feature Dependencies

**Goal:** Understand and work with features that have dependency chains.

**Prerequisites:** A workflow that has completed Feature Breakdown with multiple features

**Understanding dependency indicators:**

| Indicator | Meaning | Action |
|-----------|---------|--------|
| **⇉ Parallel** | No dependencies, start immediately | Begin Refinement right away |
| **⛓ needs FEATURE-XXX** | Blocked until FEATURE-XXX's Implement stage completes | Work on other features first |

**Workflow:**

1. **Start parallel features first** — Look for features marked "⇉ Parallel"
2. **Work through their lanes** — Refinement → Tech Design → Implement
3. **Once a blocking feature's Implement is done** — dependent features unlock
4. **Check dependency badge** — it changes from "⛓ needs..." to show unblocked status
5. **Continue with dependent features** — they can now start Refinement

**Example dependency chain:**
```
FEATURE-A (⇉ Parallel)     ——→ complete Implement ——→ unlocks FEATURE-C
FEATURE-B (⇉ Parallel)     ——→ complete Implement ——→ unlocks FEATURE-C  
FEATURE-C (⛓ needs A, B)   ——→ now starts Refinement
FEATURE-D (⛓ needs C)      ——→ waits for FEATURE-C Implement
```

**Tip:** Maximize parallelism by starting all "⇉ Parallel" features simultaneously before touching dependent features.

---

## Scenario 4: Reviewing and Tracking Deliverables

**Goal:** Find and review all artifacts generated during a workflow.

**Steps:**

1. On your workflow card, scroll down to the **"Deliverables"** panel
2. Click the **▾** toggle to expand it (if collapsed)
3. The panel shows a count badge (e.g., "52") indicating total deliverables

**Browsing deliverables:**

1. **SHARED DELIVERABLES** section shows workflow-level files:
   - 📁 `wf-008-knowledge-extraction/` — main workflow folder
   - 💡 `new idea.md` — your original idea
   - 💡 `idea-summary-v1.md` — AI-refined idea
   - 📋 `requirement-details.md` — formal requirements

2. **FEATURE-XXX** sections show per-feature files:
   - 📋 `specification.md` — feature specification
   - 📋 `technical-design.md` — architecture decisions
   - 💻 Code files (SKILL.md, implementation)
   - 📊 `acceptance-test-report.md` — test results

**File paths** are shown relative to the project root, e.g.:
- `ideas/wf-008-knowledge-extraction/refined-idea/idea-summary-v1.md`
- `requirements/EPIC-050/FEATURE-050-A/specification.md`

**Tip:** Switch to FREE mode to browse and edit any deliverable file directly in the file viewer.
