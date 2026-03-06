---
name: x-ipe-tool-web-search
description: Delegate focused web research to the current coding agent's web capability, then return structured findings and citations. Use when a skill needs industry best practices, standards, competitor patterns, or library/API guidance from the web. Triggers on requests like "web search", "research topic", "find best practices", "search the web".
---

# Web Search Tool

## Purpose

AI Agents follow this skill to perform focused external research by:
1. Determining whether a question is appropriate for web research
2. Delegating search and retrieval to the current agent's web capability
3. Synthesizing findings into reusable principles with citations

---

## Important Notes

BLOCKING: Use this skill ONLY for general knowledge topics such as industry standards, best practices, regulations, competitor patterns, or public API/library guidance.

BLOCKING: Do NOT use this skill for project-internal questions about repository code, local files, workflow state, or unpublished requirements.

CRITICAL: Prefer the current coding agent's native web capability first. Examples include built-in web search, internet-enabled fetch tools, or dedicated browsing/fetch tools exposed by the agent runtime.

CRITICAL: Keep research bounded. Default to 3 useful sources maximum unless the caller explicitly needs more.

---

## About

This tool skill standardizes how X-IPE skills ask an agent to perform public web research. It does not invent a separate crawler or search engine. Instead, it tells the executing agent to use whatever web capability the CLI/runtime already provides, then normalize the result into a compact, reusable structure.

**Key Concepts:**
- **General Knowledge Request** — A topic that can be answered from public web sources without needing project-private context
- **Agent Web Capability** — Any built-in web search, browsing, fetch, or retrieval ability available to the current CLI agent
- **Seed URLs** — Caller-provided links that should be fetched before broader search
- **Recommended Principles** — Actionable, caller-friendly takeaways extracted from the research findings

---

## When to Use

```yaml
triggers:
  - "web search"
  - "research topic"
  - "find best practices"
  - "search the web"
  - "research common principles"
  - "research industry standards"

not_for:
  - "Project-internal code or file questions — use repo search or explore instead"
  - "Autonomous conflict or routing resolution — use x-ipe-tool-decision-making"
```

---

## Input Parameters

```yaml
input:
  operation: "research_topic"
  research_request:
    topic: "short topic name"
    goal: "what the caller needs to learn"
    questions: ["specific question 1", "specific question 2"]
    seed_urls: ["https://..."]
    preferred_source_types: ["official-docs", "standards", "vendor-docs", "reputable-guides"]
    max_sources: 3
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller specifies the operation">
    <validation>MUST equal `research_topic`.</validation>
  </field>

  <field name="research_request.topic" source="Caller provides the public topic to research">
    <validation>MUST be non-empty and MUST NOT reference project-private files or code.</validation>
  </field>

  <field name="research_request.goal" source="Caller provides why the research is needed">
    <validation>MUST be non-empty.</validation>
  </field>

  <field name="research_request.questions">
    <steps>
      1. IF caller provided explicit questions → use them.
      2. ELSE derive 2-3 focused questions from topic + goal.
    </steps>
  </field>

  <field name="research_request.seed_urls">
    <steps>
      1. IF caller provided seed URLs → fetch them first.
      2. ELSE use the agent's native web capability to discover candidate sources.
    </steps>
  </field>

  <field name="research_request.max_sources">
    <steps>
      1. IF caller provided a value → use it.
      2. ELSE default to 3.
      3. Cap at 5 to keep research bounded.
    </steps>
  </field>
</input_init>
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>General topic identified</name>
    <verification>research_request.topic is public/general knowledge, not project-internal</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Research goal provided</name>
    <verification>research_request.goal explains what the caller needs from the research</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Web capability available</name>
    <verification>The executing agent has at least one web-capable search/fetch mechanism available</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: research_topic

**When:** A calling skill needs external research on a public topic such as standards, best practices, competitor patterns, or public API/library usage.

```xml
<operation name="research_topic">
  <action>
    1. Validate the request:
       - Confirm topic and goal are present.
       - Reject the request if it is project-specific or references private repo state.

    2. Build the research plan:
       - Normalize the questions list.
       - If seed URLs were provided, use them first.
       - Else formulate 1-2 focused search prompts from topic + goal.
       - Prefer the current agent's native web capability to discover authoritative sources.

    3. Gather sources:
       - Fetch or read the selected sources with the available web capability.
       - Prioritize official docs, standards bodies, regulators, major vendor docs, and reputable engineering references.
       - Exclude duplicates, irrelevant pages, and low-signal summaries.
       - Keep at most {max_sources} useful sources.

    4. Extract findings:
       - Capture per-source notes: title, URL, authority type, and the findings relevant to the caller's questions.
       - Note disagreements or uncertainty across sources.

    5. Synthesize the result:
       - Consolidate recurring findings into key_findings.
       - Convert those findings into recommended_principles the caller can apply immediately.
       - Return concise citations so downstream skills can reference them.
    </action>
  <constraints>
    - BLOCKING: Fail with `WEB_SEARCH_NOT_APPROPRIATE` if the request is project-specific
    - BLOCKING: Fail with `WEB_CAPABILITY_UNAVAILABLE` if the executing agent cannot reach any web capability
    - CRITICAL: Do not exceed 5 fetched sources in one call
    - CRITICAL: Prefer authoritative sources even if they are less concise than blog summaries
  </constraints>
  <output>operation_output with findings, recommended principles, and source citations</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    topic: "researched topic"
    goal: "caller goal"
    key_findings:
      - summary: "finding"
        supports_questions: ["question 1"]
    recommended_principles:
      - "actionable principle"
    sources:
      - title: "source title"
        url: "https://..."
        authority: "official-docs | standards | vendor-docs | reputable-guide"
        notes: "why this source was used"
    uncertainties:
      - "open question or disagreement"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Request Validated</name>
    <verification>General/public topic confirmed and request rejected if project-specific</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Bounded Source Set Selected</name>
    <verification>Candidate sources were prioritized and limited to configured maximum</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Structured Findings Returned</name>
    <verification>operation_output includes key_findings, recommended_principles, and sources or a clear failure reason</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `WEB_SEARCH_NOT_APPROPRIATE` | Request is project-specific or private | Use repository exploration tools instead of web search |
| `WEB_CAPABILITY_UNAVAILABLE` | Current agent/CLI has no usable web capability | Fall back to internal knowledge only or run on a web-capable agent |
| `NO_USEFUL_SOURCES` | Search produced no relevant authoritative sources | Narrow the topic, add seed URLs, or retry with sharper questions |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/research-summary.md` | Optional markdown structure for callers that want to embed research findings verbatim |

---

## Examples

See `.github/skills/x-ipe-tool-web-search/references/examples.md` for usage examples.
