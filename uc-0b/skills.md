# skills.md
# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and parses its content into structured, sequentially numbered sections.
    input: Document file path string reflecting the input policy text.
    output: A structured array/list of clause dictionaries, each containing the clause number and textual content.
    error_handling: Rejects the process if the file is missing or throws an error if it lacks recognizable numbered clauses.

  - name: summarize_policy
    description: Ingests structured policy sections and generates a compliant summary explicitly preserving verbatim meaning.
    input: A structured list of clause objects output by retrieve_policy.
    output: A text string structured to contain the summary mapping exactly against every numbered clause.
    error_handling: Throws a validation error if output drops any defined clauses, softens binding verbs, or loses explicitly required conditions like joint approvals.
