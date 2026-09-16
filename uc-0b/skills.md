# skills.md — UC-0B Policy Summary Skills

retrieve_policy:
  description: >
    Load the policy_hr_leave.txt file and return its contents as structured
    numbered policy sections. Preserve the original clause numbers and wording
    needed to verify requirements.

  input:
    - policy_hr_leave.txt

  output:
    - structured policy sections with clause references

  rules:
    - "Use only the supplied policy file."
    - "Preserve clause numbers exactly."
    - "Do not add external information or assumptions."

summarize_policy:
  description: >
    Produce a concise policy summary from the structured policy sections while
    preserving every required condition, requirement, approval authority,
    deadline, limit, exception, and consequence.

  input:
    - structured policy sections

  output:
    - summary with clause references for all ten mandatory clauses

  mandatory_clauses:
    - "2.3 — 14-day advance notice using Form HR-L1"
    - "2.4 — written approval from the direct manager before leave; verbal approval is not valid"
    - "2.5 — unapproved absence is recorded as LOP regardless of subsequent approval"
    - "2.6 — maximum 5 days carry-forward; excess days forfeited on 31 December"
    - "2.7 — carry-forward days must be used January–March or are forfeited"
    - "3.2 — 3 or more consecutive sick days requires a medical certificate within 48 hours of returning"
    - "3.4 — sick leave immediately before or after a public holiday or annual leave requires a certificate regardless of duration"
    - "5.2 — LWP requires approval from both the Department Head and HR Director; manager approval alone is insufficient"
    - "5.3 — LWP exceeding 30 continuous days requires Municipal Commissioner approval"
    - "7.2 — leave encashment during service is not permitted under any circumstances"

  rules:
    - "Every mandatory clause must appear in the final summary."
    - "Preserve all conditions in multi-condition requirements."
    - "Do not weaken mandatory requirements."
    - "Do not invent information or add standard HR practices."
    - "If meaning cannot be preserved safely, quote the source wording and flag the clause for review."
