# Web Search Tool - Examples

---

## Example 1: Research authentication principles during ideation

**Input:**
```yaml
operation: research_topic
research_request:
  topic: "consumer authentication for mobile apps"
  goal: "Identify common principles for a new fintech app idea"
  questions:
    - "What authentication patterns are considered standard for consumer apps?"
    - "When is MFA recommended?"
    - "What usability trade-offs are common?"
  max_sources: 3
```

**Expected Result:**
- Agent uses its native web capability to fetch 2-3 strong public sources
- Key findings summarized with citations
- Recommended principles such as MFA for risky actions, device biometrics as convenience layer, and recovery-path requirements

---

## Example 2: Research from seed URLs

**Input:**
```yaml
operation: research_topic
research_request:
  topic: "OAuth 2.1 for SaaS integrations"
  goal: "Understand current best practices for third-party account linking"
  questions:
    - "Which grant flow is preferred for browser-based apps?"
  seed_urls:
    - "https://oauth.net/2.1/"
    - "https://datatracker.ietf.org/doc/html/rfc6749"
```

**Expected Result:**
- Seed URLs fetched before broader discovery
- Findings cite the provided standards first
- Output highlights actionable principles for the calling skill

---

## Example 3: Reject project-specific request

**Input:**
```yaml
operation: research_topic
research_request:
  topic: "How does workflow_manager_service.py currently migrate templates?"
  goal: "Explain the repository's current behavior"
```

**Expected Result:**
```yaml
operation_output:
  success: false
  result: {}
  errors:
    - code: WEB_SEARCH_NOT_APPROPRIATE
      message: Use repository exploration tools for project-internal questions.
```
