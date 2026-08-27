uc_id: UC-0B
title: Policy Summary Without Meaning Loss

objective: >
  Generate a summary of HR policy documents that preserves all clause-level obligations,
  conditions, and legal intent without omission, softening, or scope expansion.

framework: RICE

reach:
  description: >
    Applies to HR policy documents (e.g., leave policies) containing structured clauses.
    Used for compliance, HR operations, and employee communication.
  scope: document-level summarization

impact:
  description: >
    Very high impact. Any loss of obligation, condition, or authority can lead to
    policy misinterpretation and compliance risk.
  goals:
    - Preserve all clauses (no omission)
    - Retain all conditions in multi-condition clauses
    - Maintain binding strength of verbs (must, requires, not permitted)
    - Avoid hallucination or scope expansion

confidence:
  risks:
    - Clause omission
    - Dropping conditions (especially multi-approver requirements)
    - Obligation softening (must → should)
    - Scope bleed (adding generic HR language)
  mitigations:
    - Mandatory clause inventory mapping
    - Clause-by-clause summarization
    - Verbatim fallback when summarization risks meaning loss
    - Explicit validation step before output

effort:
  level: medium
  components:
    - Clause extraction
    - Structured parsing
    - Controlled summarization
    - Validation against clause inventory

ground_truth_clauses:
  - clause: "2.3"
    obligation: "14-day advance notice required"
    verb: "must"

  - clause: "2.4"
    obligation: "Written approval required before leave commences. Verbal not valid."
    verb: "must"

  - clause: "2.5"
    obligation: "Unapproved absence = LOP regardless of subsequent approval"
    verb: "will"

  - clause: "2.6"
    obligation: "Max 5 days carry-forward. Above 5 forfeited on 31 Dec."
    verb: "may / are forfeited"

  - clause: "2.7"
    obligation: "Carry-forward days must be used Jan–Mar or forfeited"
    verb: "must"

  - clause: "3.2"
    obligation: "3+ consecutive sick days requires medical cert within 48hrs"
    verb: "requires"

  - clause: "3.4"
    obligation: "Sick leave before/after holiday requires cert regardless of duration"
    verb: "requires"

  - clause: "5.2"
    obligation: "LWP requires Department Head AND HR Director approval"
    verb: "requires"

  - clause: "5.3"
    obligation: "LWP >30 days requires Municipal Commissioner approval"
    verb: "requires"

  - clause: "7.2"
    obligation: "Leave encashment during service not permitted under any circumstances"
    verb: "not permitted"

enforcement_rules:
  - Every clause listed in ground_truth_clauses must appear in the summary
  - Clause numbers must be preserved in output
  - Multi-condition clauses must retain ALL conditions (e.g., both approvers in 5.2)
  - Binding verbs must not be softened (must ≠ should)
  - No additional assumptions or external HR practices allowed
  - If summarization risks meaning loss → quote clause verbatim and flag it

validation_checks:
  - All 10 clauses are present
  - No clause meaning is altered
  - No condition is dropped
  - No new information added
  - Verbs retain original strength

output_format:
  structure: >
    Numbered summary aligned to clause numbers (e.g., 2.3, 2.4, etc.)
  requirements:
    - Each clause summarized in 1–2 lines
    - Include clause number
    - Preserve conditions and authority roles
    - Flag clauses quoted verbatim if needed