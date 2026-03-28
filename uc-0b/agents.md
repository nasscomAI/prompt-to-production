# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: "UC-0B policy summarization agent. Operates on one HR leave policy text file and produces a clause-preserving summary."

intent: "Given policy_hr_leave.txt, output a summary that includes every numbered ground-truth clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2), retains all obligation conditions, avoids adding extraneous content, and flags verbatim quotes when meaning preservation would otherwise be lost."

context: "Input is only ../data/policy-documents/policy_hr_leave.txt and its extracted numbered sections; do not use external knowledge; do not introduce scope bleed language not present in the source."

enforcement:
  - "Every numbered clause must be present in the summary (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)."
  - "Multi-condition obligations must preserve all conditions; never drop one silently."
  - "Never add information not present in the source document."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it."
  - "Clause 5.2 must explicitly retain requirement for both Department Head and HR Director approvals."
  - "Do not include scope bleed phrases not in source: e.g. 'as is standard practice', 'typically in government organisations', 'employees are generally expected to'."

