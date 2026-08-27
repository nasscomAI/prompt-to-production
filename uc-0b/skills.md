skills:

- name: retrieve_policy
  description: Load the HR leave policy from the provided text file and return its numbered clauses as structured sections.
  input: A policy file path pointing to the source .txt file.
  output: A structured list of numbered policy sections containing each clause reference and its original content.
  error_handling: If the file cannot be read or a numbered clause cannot be identified reliably, report the problem and do not invent or reconstruct missing policy content.

- name: summarize_policy
  description: Produce a clause-referenced summary of the structured policy while preserving every obligation and condition.
  input: Structured numbered policy sections returned by retrieve_policy.
  output: A concise summary containing all required clause references and preserving binding verbs, conditions, approvers, deadlines, thresholds, and prohibitions from the source.
  error_handling: If a clause cannot be summarized without changing its meaning, quote that clause verbatim and flag it instead of guessing or omitting it.