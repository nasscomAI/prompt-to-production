skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured, numbered sections to prevent clause omission. Must extract all 10 core clauses from the UC-0B HR Leave Policy.
    input: File path to the policy document (.txt).
    output: Structured representation of numbered sections and clauses, including all 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    enforcement: Every numbered clause must be extracted. If any clause is missing, retrieval has failed.
    error_handling: If the file is not found or unreadable, return an error indicating the document could not be accessed. If extracted sections do not contain all 10 clauses, flag as incomplete retrieval.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, fully preserving all multi-condition obligations and avoiding scope bleed. Must preserve exact binding verbs and approver names.
    input: Structured policy sections containing the 10 core clauses.
    output: Compliant summary text containing all 10 core clauses with full preservation of multi-condition obligations.
    critical_constraints:
      - Clause 2.3: Preserve "14-day advance notice" (binding verb: must)
      - Clause 2.4: Preserve "Written (not verbal) approval" requirement before leave commences
      - Clause 2.5: Preserve "Unapproved absence = LOP regardless of subsequent approval"
      - Clause 2.6: Preserve "Max 5 days carry-forward; above 5 forfeited on 31 Dec"
      - Clause 2.7: Preserve "Carry-forward days must be used Jan–Mar or forfeited"
      - Clause 3.2: Preserve "3+ consecutive sick days requires medical cert within 48hrs"
      - Clause 3.4: Preserve "Sick leave before/after holiday requires cert regardless of duration"
      - Clause 5.2: CRITICAL — Preserve "LWP requires BOTH Department Head AND HR Director approval" (both approvers must be named)
      - Clause 5.3: Preserve "LWP >30 days requires Municipal Commissioner approval"
      - Clause 7.2: Preserve "Leave encashment during service not permitted under any circumstances"
    failure_modes_to_detect_and_avoid:
      - "Clause omission: Missing or incomplete numbered clauses"
      - "Condition drop: Preserving an obligation but losing one of its conditions (e.g., Clause 5.2 loses 'HR Director' approval)"
      - "Scope bleed: Adding phrases like 'as is standard practice', 'typically in government', 'employees are generally expected to' — these are hallucinations"
      - "Obligation softening: Changing binding verbs (must → may, will → could) or hedging language"
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it. If any clause is omitted or any multi-condition obligation has conditions dropped, summarization has failed.
