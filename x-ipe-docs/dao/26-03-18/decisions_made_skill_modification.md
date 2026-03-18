## 2026-03-18 | Apply Lessons to Extractor Skill

**Context:**
- Source: human
- Task: TASK-TBD (will be created)
- Workflow: skill-modification
- Calling skill: N/A

**Message:**
Apply 2 lessons learned to the extractor skill. Work in the CANDIDATE folder first, then merge to production.
- Lesson 1: Session-scoped screenshots (inside session folder, not flat path)
- Lesson 2: Post-generation session cleanup (remove entire session folder on success, preserve on failure)

**Instruction Units:**

### Unit 0: Apply lessons to extractor skill
**Disposition:** instruction
**Suggested Skill:** x-ipe-meta-skill-creator (strong match)
**Rationale:** Skill modification task. Per governance, ANY modification to defined skill types MUST go through x-ipe-meta-skill-creator to ensure validation and proper process. User provided specific file changes for 4 files in candidate folder.
**Content:** You are instructed to apply 2 lessons to the x-ipe-task-based-application-knowledge-extractor skill by editing 4 candidate files (handoff-protocol.md, execution-procedures.md, SKILL.md, checkpoint-manifest.md), then copying to production. Follow x-ipe-meta-skill-creator process.

**Execution Plan:**
- Strategy: sequential
- Groups: [[0]]
- Rationale: Single instruction unit — apply lessons through proper skill modification process

**Confidence:** 0.9
**Fallback Required:** false
