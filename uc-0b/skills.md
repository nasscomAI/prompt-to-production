# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses its content into structured, numbered sections.
    input: File path (string) to the source policy text file.
    output: A list of objects, each containing a 'clause_id' (e.g., 2.3) and the raw 'text' of that clause.
    error_handling: Returns a clear error if the file is missing or unreadable. If section headers are missing, it attempts to group content by paragraph.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary while preserving all conditions and binding verbs.
    input: A list of structured clause objects from retrieve_policy.
    output: A multi-line string where every mandatory clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is summarized or quoted verbatim with its clause reference.
    error_handling: If a multi-condition obligation (like Clause 5.2) cannot be summarized without dropping a condition, it must quote the clause verbatim and flag it for review.
