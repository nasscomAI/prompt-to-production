# skills.md — UC-0B Summary That Changes Meaning
# Workshop: RICE prompt → generated draft → manual CRAFT refinement

skills:
  - name: retrieve_policy
    description: Loads policy_hr_leave.txt and returns content as structured OrderedDict of clause IDs to verbatim text with section context.
    input: Path to policy_hr_leave.txt (UTF-8 text file with numbered clauses 1.1–8.2).
    output: OrderedDict `clause_id → {section: str, text: str}` plus `_meta` header; preserves exact clause text for citation.
    error_handling: File missing → FileNotFoundError with path; no clauses matched → ValueError "No numbered clauses found"; preserves original whitespace for verbatim fallback.

  - name: summarize_policy
    description: Takes structured sections and produces compliant summary with Clause X.Y references, preserving every numbered clause and all binding conditions.
    input: OrderedDict from retrieve_policy (29 clauses inc. _meta).
    output: String where each line starts `Clause X.Y:` followed by obligation preserving binding verbs (must/requires/will/not permitted/may/are forfeited) and all conditions; critical 10 flagged [VERBATIM].
    error_handling: If clause cannot be shortened without dropping condition (e.g., 5.2 both approvers, 2.4 written+verbal) → outputs verbatim + [VERBATIM]; never invents conditions; never omits a clause; never hedges.

  - name: verification
    description: Checks summary against enforcement before writing.
    input: Generated summary string.
    output: Pass/fail with list of checks (every clause present, 10 critical verbatim present, no banned phrases).
    error_handling: If any clause missing or banned phrase found → raise ValueError with details; else allow write.

notes: >
  CRAFT loop: naive "Summarize the policy" → omitted 2.5, dropped 5.2 second approver, added "typically" → fixed via verbatim critical map + every-clause loop + banned-phrase filter. Verified 29 clauses, 10 critical PASS, no bleed.
