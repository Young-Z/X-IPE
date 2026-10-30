# Knowledge Referencer Skill — Examples

## Example 1: Search for "authentication" Across KB

**Query:** "authentication"
**Scope:** all
**include_user_manual:** true (but no user manual KB exists)

**Execution:**
```
1. Phase 1 - Gather Context:
   - query: "authentication"
   - search_path: x-ipe-docs/knowledge-base/
   - Checked for user manual KB: no 04-core-features/ or 01-overview.md found
   - has_user_manual: false
   - user_manual_applicable: false

2. Phases 2-4: SKIP (no ambiguity, no design decisions, single approach)

3. Step 5.1 - Full-Text Search:
   - Grep for "authentication" in x-ipe-docs/knowledge-base/**/*.md
   - Matches found:
     - x-ipe-docs/knowledge-base/app-myapp/02-features/auth-module.md
       Line 12: "The authentication module handles login, logout, and token refresh."
       Context: Describes JWT-based auth flow
     - x-ipe-docs/knowledge-base/app-myapp/03-architecture/security.md
       Line 45: "Authentication is handled via OAuth2 with PKCE."
       Context: Describes security architecture
     - x-ipe-docs/knowledge-base/app-myapp/02-features/user-management.md
       Line 8: "User management depends on authentication service for identity verification."
       Context: References auth as a dependency
   - full_text_matches: 3 files

4. Step 5.2 - Ontology Search (MANDATORY):
   - Loaded x-ipe-tool-reference-ontology
   - Search for "authentication" in ontology
   - Matches:
     - entity_id: "ENT-AUTH-001"
       label: "Authentication Module"
       node_type: "component"
       source_files: [auth-module.md, security.md]
       dimensions: [security, identity, access-control]
       relevance: 0.95
     - entity_id: "ENT-OAUTH-002"
       label: "OAuth2 Integration"
       node_type: "feature"
       source_files: [security.md, integration-guide.md]
       dimensions: [security, external-integration]
       relevance: 0.82
   - ontology_matches: 2 entities

5. Step 5.3 - User Manual Lookup: SKIPPED (no user manual KB)
   - user_manual_matches: []

6. Step 5.4 - Combine & Consolidate:
   - All source files collected:
     - auth-module.md: found by full-text + ontology → rank: HIGH (2 methods)
     - security.md: found by full-text + ontology → rank: HIGH (2 methods)
     - user-management.md: found by full-text only → rank: STANDARD (1 method)
     - integration-guide.md: found by ontology only → rank: STANDARD (1 method)
   - Deduplicated: 4 unique files
   - Ranked: auth-module.md and security.md first (2 hits each)

Output Result:
  category: standalone
  status: completed
  total_results: 4
  consolidated_results:
    full_text_matches: [3 entries]
    ontology_matches: [2 entities]
    user_manual_matches: []
    summary: |
      Authentication in the KB is documented across 4 files. The core
      authentication module (auth-module.md) uses JWT-based login/logout/refresh.
      The security architecture (security.md) implements OAuth2 with PKCE.
      User management depends on authentication for identity verification.
      The ontology tags this under security, identity, and access-control dimensions.
```

---

## Example 2: Lookup "how to configure export settings" (with User Manual)

**Query:** "how to configure export settings"
**Scope:** all
**include_user_manual:** true

**Execution:**
```
1. Phase 1 - Gather Context:
   - query: "how to configure export settings"
   - search_path: x-ipe-docs/knowledge-base/
   - Checked for user manual KB: found 04-core-features/ directory
   - has_user_manual: true
   - user_manual_applicable: true

2. Phases 2-4: SKIP

3. Step 5.1 - Full-Text Search:
   - Grep for keywords: "configure", "export", "settings"
   - Matches found:
     - x-ipe-docs/knowledge-base/app-myapp/02-features/export-feature.md
       Line 23: "Export settings are configured via the settings panel."
       Context: Describes export configuration options (format, destination, scheduling)
     - x-ipe-docs/knowledge-base/app-myapp/03-architecture/config-system.md
       Line 67: "The settings system supports export format configuration."
       Context: Describes how configuration values are stored and loaded
   - full_text_matches: 2 files

4. Step 5.2 - Ontology Search (MANDATORY):
   - Loaded x-ipe-tool-reference-ontology
   - Search for "export settings"
   - Matches:
     - entity_id: "ENT-EXPORT-010"
       label: "Export Configuration"
       node_type: "feature"
       source_files: [export-feature.md]
       dimensions: [data-export, configuration, user-settings]
       relevance: 0.91
   - ontology_matches: 1 entity

5. Step 5.3 - User Manual Lookup:
   - Loaded x-ipe-tool-reference-user-manual
   - Searched for "how to configure export settings"
   - Matches:
     - file_path: x-ipe-docs/knowledge-base/app-myapp/04-core-features/export.md
       title: "Configuring Export Settings"
       relevance_score: 0.93
       interaction_pattern: |
         1. Navigate to Settings > Export
         2. Select output format (CSV, JSON, PDF)
         3. Choose destination folder
         4. Set schedule (manual, daily, weekly)
         5. Click Save
   - user_manual_matches: 1 entry

6. Step 5.4 - Combine & Consolidate:
   - All source files collected:
     - export-feature.md: found by full-text + ontology → rank: HIGH (2 methods)
     - export.md (manual): found by user manual → rank: STANDARD (1 method)
     - config-system.md: found by full-text only → rank: STANDARD (1 method)
   - Deduplicated: 3 unique files
   - Ranked: export-feature.md first (2 hits)

Output Result:
  category: standalone
  status: completed
  total_results: 3
  consolidated_results:
    full_text_matches: [2 entries]
    ontology_matches: [1 entity]
    user_manual_matches: [1 entry]
    summary: |
      Export settings are configured via the Settings > Export panel. Users can
      select output format (CSV, JSON, PDF), choose a destination folder, and
      set scheduling (manual/daily/weekly). The export feature is documented in
      export-feature.md (feature spec) and export.md (user manual with step-by-step
      instructions). The configuration system stores these values as described
      in config-system.md.
```

---

## Example 3: Scoped Search in a Specific KB Folder

**Query:** "database migration"
**Scope:** "app-billing"
**include_user_manual:** false

**Execution:**
```
1. Phase 1 - Gather Context:
   - query: "database migration"
   - kb_scope: "app-billing"
   - search_path: x-ipe-docs/knowledge-base/app-billing/
   - Verified path exists: YES
   - include_user_manual: false → user_manual_applicable: false

2. Phases 2-4: SKIP

3. Step 5.1 - Full-Text Search:
   - Grep for "database", "migration" in x-ipe-docs/knowledge-base/app-billing/**/*.md
   - Matches found:
     - x-ipe-docs/knowledge-base/app-billing/03-architecture/data-layer.md
       Line 34: "Database migrations are managed via Alembic."
       Context: Describes migration tooling and conventions
   - full_text_matches: 1 file

4. Step 5.2 - Ontology Search (MANDATORY):
   - Loaded x-ipe-tool-reference-ontology
   - Search for "database migration" scoped to app-billing
   - Matches:
     - entity_id: "ENT-DB-MIGRATE-005"
       label: "Billing DB Migration"
       node_type: "process"
       source_files: [data-layer.md]
       dimensions: [database, infrastructure, billing]
       relevance: 0.88
   - ontology_matches: 1 entity

5. Step 5.3 - User Manual Lookup: SKIPPED (include_user_manual is false)
   - user_manual_matches: []

6. Step 5.4 - Combine & Consolidate:
   - Source files:
     - data-layer.md: found by full-text + ontology → rank: HIGH (2 methods)
   - Deduplicated: 1 unique file

Output Result:
  category: standalone
  status: completed
  total_results: 1
  consolidated_results:
    full_text_matches: [1 entry]
    ontology_matches: [1 entity]
    user_manual_matches: []
    summary: |
      Database migrations for the billing app are managed via Alembic, as
      documented in data-layer.md. The ontology classifies this under database,
      infrastructure, and billing dimensions. Search was scoped to app-billing only.
```
