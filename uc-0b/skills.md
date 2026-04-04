skills:
  - name: retrieve_policy
    description: Ingests the raw policy text file and parses it into a structured format organized by numbered section headers for precise clause mapping.
    input:
      type: file
      format: A .txt file containing the leave policy text.
    output:
      type: list
      format: A structured list of objects containing clause numbers and their corresponding raw text.
    error_handling: Aborts and logs an error if the input file is missing or if the structure fails to provide the 10 mandatory ground-truth clauses.

  - name: summarize_policy
    description: Condenses structured policy sections into a summary that preserves all core obligations, multi-condition approvals, and binding verbs without omission.
    input:
      type: list
      format: Structured numbered sections retrieved from the policy document.
    output:
      type: string
      format: A text summary referencing all 10 clauses, highlighting verbatim quotes for complex conditions.
    error_handling: Flags and quotes any section verbatim where summarization would result in meaning loss; explicitly checks for and restores dropped conditions in multi-approver clauses like 5.2.