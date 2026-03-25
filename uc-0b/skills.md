# skills.md

skills:
  - name: "retrieve_policy"
    description: "Loads the source .txt policy file and parses it into a structured set of numbered clauses (e.g., Clause 5.2)."
    input: "Path to the source .txt policy file."
    output: "List of dictionaries, each containing 'clause_id' and 'text'."
    error_handling: "Raises FileNotFoundError if the path is invalid and logs warning if numbering structure is inconsistent."

  - name: "summarize_policy"
    description: "Evaluates the structured clauses and produces a summary that preserves all core obligations and conditions using the RICE framework."
    input: "List of structured sections from retrieve_policy."
    output: "A well-formatted summary string where every clause is referenced."
    error_handling: "Flags sections as 'COMPLEX_CLAUSE' and quotes them verbatim if they cannot be safely compressed without meaning loss."
