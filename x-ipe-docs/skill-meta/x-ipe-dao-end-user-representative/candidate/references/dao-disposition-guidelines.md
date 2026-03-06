# Disposition Guidelines

Use this guide when `x-ipe-dao-end-user-representative` chooses how to represent human intent at a touchpoint.

| Disposition | Use When | Avoid When | Output Style |
|-------------|----------|------------|--------------|
| `answer` | The skill can safely answer directly from current context | Detailed downstream execution state is needed | Clear, concise answer |
| `clarification` | The request is ambiguous or underspecified | The skill already has enough context to respond | Short narrowing question |
| `reframe` | The user is asking at the wrong abstraction level | A direct answer is already sufficient | Redirect toward the more useful framing |
| `critique` | The request or plan needs constructive challenge | The user only needs a simple factual answer | Specific, respectful concerns |
| `instruction` | The skill should provide next-step guidance | The downstream agent should take over immediately | Actionable steps |
| `approval` | The best intervention is concise approval-like guidance | Real human authorization or audit record is required | Brief proceed guidance with caveat |
| `pass_through` | The downstream agent is best positioned to answer | The skill can resolve the touchpoint itself | Handoff framing that preserves user intent |

## Selection Heuristics

1. Prefer the smallest helpful intervention.
2. Use `pass_through` for detailed downstream status or implementation questions.
3. Use `clarification` before `critique` when ambiguity is the real blocker.
4. Never claim human approval occurred; `approval` is guidance, not an authorization artifact.
5. Keep `rationale_summary` short and bounded.
