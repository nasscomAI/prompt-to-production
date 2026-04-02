# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path to the policy document (.txt format).
    output: Structured representation (e.g., list or JSON) containing numbered sections/clauses and their corresponding text.
    error_handling: Return an error if the file is not found or cannot be parsed into structured sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, ensuring no multi-condition obligations are dropped and no meaning is lost.
    input: Structured sections/clauses (output from retrieve_policy).
    output: A summarized text document with explicit clause references for each obligation.
    error_handling: If a clause cannot be summarized without losing meaning or dropping a condition, quote the clause verbatim and flag it in the summary.
