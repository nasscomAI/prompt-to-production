skills:
name: retrieve_policy
description: Loads the HR leave policy text file and returns its content as structured numbered sections.
input: |
Text file at ../data/policy-documents/policy_hr_leave.txt containing policy clauses.
output: |
Structured object with numbered clauses and their corresponding text.
error_handling: |
If the file is missing or unreadable, return an error message.
If clauses cannot be parsed into numbered sections, flag the document for manual review.
Prevent clause omission by ensuring all 10 clauses are extracted.
Do not add or invent clauses beyond the source document.
name: summarize_policy
description: Produces a compliant summary of the HR leave policy with clause references, preserving obligations and binding verbs.
input: |
Structured object of numbered clauses with text from retrieve_policy.
output: |
Text file at uc-0b/summary_hr_leave.txt containing summaries of all clauses with references.
error_handling: |
If summarization risks meaning loss, quote the clause verbatim and flag it.
If multi-condition obligations are present, ensure all conditions are preserved; flag if any are dropped.
Prevent scope bleed by rejecting phrases not in the source document.
Prevent obligation softening by preserving binding verbs exactly.
If any clause is missing in the summary, flag the output as incomplete.