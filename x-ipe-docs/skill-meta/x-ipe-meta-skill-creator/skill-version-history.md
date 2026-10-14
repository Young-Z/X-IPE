---
skill_name: x-ipe-meta-skill-creator
current_version: 1.3.0

versions:
  - version: 1.3.0
    date: 2026-10-14
    author: GitHub Copilot
    changes:
      - type: enhancement
        description: "Exact R2 creator consumer integration: guarded installed lesson select/settle calls and goal-aware task template with single-owner handoff"
      - type: compatibility
        description: "Validator accepts only the established Engineer assistant identity; publisher unchanged; hybrid mode follows current specification/UI"
    test_results:
      before_passed: 421
      before_failed: 0
      after_unchanged_suite_passed: 419
      after_unchanged_suite_failed: 2
      obsolete_pre_promotion_assertions: 2
      installed_routed_passed: 419
      installed_routed_failed: 0
      installed_routed_deselected: 2
      installed_identity_negative_controls_passed: 4
      tests_modified: false
    publication:
      state: published
      method: apply_patch
      receipt: x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/publication-receipt-TASK-6749-R2.json
      review: x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/independent-review-promotion-TASK-6749-R2.md
      candidate_hash: 2716c799849a49686a4c83c86c35ba5c2f84e41d870f25258e359906141fbcf8
      production_distributable_hash: 2716c799849a49686a4c83c86c35ba5c2f84e41d870f25258e359906141fbcf8
      distributable_files: 33
      distributable_byte_parity: true
      unmanaged_compiled_caches_preserved: 2
      real_lesson_settlement: false
      full_task_completion_claimed: false
  - version: 1.2.1
    date: 2026-10-14
    author: GitHub Copilot
    changes:
      - type: compatibility
        description: "Exact legacy quality category Operations validation; four distributable text changes, no broad identity or safety exemption"
    test_results:
      focused_passed: 184
      focused_failed: 0
      bounded_python_passed: 464
      bounded_python_failed: 0
      frontend_passed: 10
    publication:
      state: published
      method: apply_patch
      receipt: x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/publication-receipt-legacy-category-TASK-6749.yaml
      candidate_hash: 762d5ef4818aba6ca16ad1dfb75b646b74eddcc2f46f3ef90252829c5d5ea271
      distributable_files: 32
      distributable_byte_parity: true
      unmanaged_compiled_caches_preserved: 2
  - version: 1.2.0
    date: 2026-10-13
    author: GitHub Copilot
    changes:
      - type: refactoring
        description: "Promote reviewed creator foundation: concise entry, unified body ceiling, preserved subtype contracts, bounded lessons and manifest-safe validation/publication helpers"
      - type: validation
        description: "TASK-6749 sequential step 1: fresh independent review; exact 32-file parity; 3 additions, 20 changes, no removals; review metadata explicitly excluded"
    test_results:
      pass_rate: 100%
      tests_run: 163
      failed: 0
      pre_promotion: "163 passed in 1.60s"
      post_promotion: "163 passed in 1.63s"
    publication:
      state: published
      method: authorized_editor_tools
      receipt: x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/promotion-receipt.yaml
      candidate_hash: d548972671b39a8a7a0940fe30fa6d7e143b68ba32e8919b4192c640c14bca39
      production_hash: d548972671b39a8a7a0940fe30fa6d7e143b68ba32e8919b4192c640c14bca39
      byte_parity: true
      production_body_lines: 246
  - version: 1.1.0
    date: 2026-03-06
    author: Onyx
    changes:
      - type: enhancement
        description: "Add x-ipe-dao as a first-class skill type with dedicated templates"
    test_results:
      pass_rate: 100%
      tests_run: 13
  - version: 1.0.0
    date: 2026-02-06
    author: Unknown
    changes:
      - type: baseline
        description: "Existing skill creator candidate"
    test_results:
      pass_rate: 100%
      tests_run: 0
---
