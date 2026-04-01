# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads the policy document and parses it into structured numbered sections for accurate individual processing.
    input: File path to the target .txt document containing the policy.
    output: A structured dictionary mapping section and clause numbers to their raw unedited text.
    error_handling: Throws an explicit error if the format is unreadable or non-standard, preventing hallucinated context.

  - name: summarize_policy
    description: Receives the specific targeted clauses from the structured policy and produces a concise summary maintaining all original conditions.
    input: The dictionary of structured policy sections.
    output: A string containing the final generated summary, with references to every targeted clause and all dual-conditions preserved.
    error_handling: Flags clauses that are deemed ambiguous or overly complex by dumping them verbatim instead of summarising.
