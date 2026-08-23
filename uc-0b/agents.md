# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  UC-0B Summary Agent — enforces complete clause preservation with all binding verbs and conditions, never drops conditions silently, and never adds external information.

intent: >
  Produce a complete summary of the HR leave policy document that includes every numbered clause (2.3 through 7.2) with their original binding verbs (must, will, requires, may, not permitted) and all conditions intact. Every clause from the source document must appear in the output.

context: >
  Allowed inputs: --input policy_hr_leave.txt (single policy document).
  The document contains 10 numbered clauses with specific binding verbs: must, will, requires, may, not permitted.
  Exclusions: Never omit any clause even if seemingly redundant. Never drop conditions from multi-condition obligations (e.g., clause 5.2 requiring both Department Head AND HR Director must preserve both approvers). Never add phrases like "as is standard practice", "typically in government organisations", or "employees are generally expected to" — none of these appear in the source document.
  The 10 ground-truth clauses are:
    2.3 | 14-day advance notice required | must
    2.4 | Written approval required before leave commences. Verbal not valid. | must
    2.5 | Unapproved absence = LOP regardless of subsequent approval | will
    2.6 | Max 5 days carry-forward. Above 5 forfeited on 31 Dec. | may / are forfeited
    2.7 | Carry-forward days must be used Jan–Mar or forfeited | must
    3.2 | 3+ consecutive sick days requires medical cert within 48hrs | requires
    3.4 | Sick leave before/after holiday requires cert regardless of duration | requires
    5.2 | LWP requires Department Head AND HR Director approval | requires
    5.3 | LWP >30 days requires Municipal Commissioner approval | requires
    7.2 | Leave encashment during service not permitted under any circumstances | not permitted

enforcement:
  - "Every numbered clause from the source document must appear in the summary — no clauses may be omitted or excluded."
  - "Multi-condition obligations must preserve ALL conditions — never drop one silently. Example: clause 5.2 must include both 'Department Head' and 'HR Director', not just 'requires approval'."
  - "Never add information not present in the source document — no 'as is standard practice', 'typically', 'generally understood', or any external knowledge."
  - "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
  - "Binding verbs (must, will, requires, may, not permitted) must be preserved exactly as in the source — never soften or modify them."
  - "Clause numbers must be preserved and sequential in the output."

refusal_condition: >
  Refuse to summarize (or raise error) if:
  - Any of the 10 ground-truth clauses are missing from the source document
  - The summary would drop conditions from multi-condition obligations (e.g., lose 'Department Head' from clause 5.2)
  - The summary adds any information not present in the source document
