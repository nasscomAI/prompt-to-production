# skills.md — UC-0B Policy Summarizer

skills:

* name: retrieve_policy
  description: Loads the supplied policy text file and extracts its content into structured numbered sections.
  input: Path to a .txt policy document.
  output: Structured policy sections containing clause numbers and their corresponding source text.
  error_handling: If the file cannot be read or a numbered clause cannot be parsed reliably, report the problem rather than inventing missing policy content.

* name: summarize_policy
  description: Summarizes the structured policy sections while preserving every clause, binding obligation, condition, deadline, restriction, approval requirement, and consequence.
  input: Structured numbered policy sections returned by retrieve_policy.
  output: A policy summary containing clause references and meaning-preserving summaries of all numbered clauses.
  error_handling: If a clause cannot be summarized without changing or losing its meaning, preserve the original clause text and flag it for review rather than guessing.
