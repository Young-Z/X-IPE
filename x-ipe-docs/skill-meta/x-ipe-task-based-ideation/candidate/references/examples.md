# Ideation examples

## Small, clear idea

The user requests a read-only status badge with a stated audience and behavior.
Read that source and relevant existing decisions. No research or ceremonial
question is needed. The same agent checks clarity/feasibility and writes
`x-ipe-docs/ideas/{folder}/refined-idea/idea-summary-v1.md` using the summary
template. Plain Markdown is sufficient even with visualization tools enabled.
Self-check scope and links; return the original result to the lifecycle owner.
No critic agent, DoD agent, mandatory graphic, new downstream task or auto commit.

## Unclear business idea with tools available

The source contains conflicting platform goals and a real unresolved offline
requirement. Ask only the consequential question through the current interaction
policy; reuse previously supplied answers. Research the offline constraint only
if needed, using an enabled capability and citing actual sources. An enabled
diagram tool is loaded only if a flow clarifies the requested idea. Do not load
every tool or create every possible visual because it is available.
Preserve source intent, decisions, limitations and material open questions.

## No tools or missing config

Report that optional capabilities are unavailable; do not create or enable tools
configuration implicitly. Read the source, resolve material gaps and write a
plain-Markdown summary. If a necessary fact cannot be established without a
missing capability, keep that claim blocked rather than inventing research.
Preserve earlier versions and unrelated files under `refined-idea/`.

## Revision and downstream reuse

For an existing idea, change only authorized sections, retain source links and
increment the numeric version where a new summary is created. The owner verifies
the current `refine_idea` action and exact `refined-idea`/`refined-ideas-folder`
outputs in workflow-mode. Free-mode performs no app write. Mockup, architecture,
sharing and requirements are conditional suggestions, not a mandatory agent chain.
