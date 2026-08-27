skill: retrieve_policy
description: Load policy document and return structured numbered clauses
input: policy file path
output: structured numbered clauses
constraints:
- Preserve clause numbers
- Do not modify original text

skill: summarize_policy
description: Produce a compliant summary of each clause
input: structured clauses
output: clause-based summary
rules:
- Every clause must appear in summary
- Do not drop conditions
- Do not add new information
- Preserve binding verbs (must, requires, not permitted)
- If summarization changes meaning, quote clause verbatim