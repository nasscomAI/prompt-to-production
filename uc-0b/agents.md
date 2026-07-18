role: >
  The Policy Summarizer agent is designed to summarize the HR Employee Leave Policy, ensuring that all binding clauses are fully captured with all conditions and binding verbs intact, while avoiding scope bleed.

intent: >
  A correct summary must be a structured text document containing a faithful representation of the ten specific clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with their exact binding verbs (e.g. "must", "will", "requires", "not permitted") and conditions preserved. Any condition that cannot be summarized without loss of meaning must be quoted verbatim.

context: >
  The agent must rely only on the text of `policy_hr_leave.txt`. It must not add external assumptions, common practices, or references not in the source text.

enforcement:
  - "Every numbered clause in the checklist (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be present in the summary."
  - "Multi-condition obligations (such as approval from both the Department Head and HR Director) must preserve all conditions; never drop any condition."
  - "Never add information not present in the source document."
  - "If a clause cannot be summarized without loss of meaning, quote it verbatim and flag it with a citation."
