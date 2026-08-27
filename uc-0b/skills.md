# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Load a .txt policy document and return its content as structured numbered sections.
    input: Path to a .txt policy file.
    output: A list of sections, each with the section number and its list of numbered clauses with their original text preserved.
    error_handling: If the file cannot be read, return an error listing the missing path; do not proceed to summarise an empty document.

  - name: summarize_policy
    description: Produce a clause-complete, meaning-preserving summary of the structured sections with clause references.
    input: Structured sections from retrieve_policy.
    output: A text summary in which every inventoried clause appears, retains all its conditions and binding verb, and adds no external information.
    error_handling: If a clause's obligation cannot be summarised without loss, quote it verbatim and flag it for review instead of paraphrasing loosely.
