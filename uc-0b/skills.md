# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections for accurate referencing.
    input: File path to the raw .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured list or dictionary containing the parsed numbered sections and their corresponding text.
    error_handling: If the file is missing or the text cannot be parsed into numbered sections, halt execution and raise a specific error.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all clauses and multi-condition obligations.
    input: Structured numbered sections returned by the retrieve_policy skill.
    output: A compiled summary text containing explicit clause references.
    error_handling: If a clause cannot be confidently summarized without losing its meaning or conditions, quote it verbatim and append a specific flag for manual review.
