# skills.md — UC-0B HR Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and parses it into structured numbered sections.
    input: >
      A file path (str) to a policy document in text format.
    output: >
      A list of dicts, where each dict contains:
        - clause_number (str): The section or clause identifier (e.g., "2.3").
        - text (str): The raw text content of that specific clause.
    error_handling: >
      If the file is missing or unreadable, raise a clear error with the file path.
      If the text structure does not allow for numbered clause extraction, 
      return an error indicating the format is unsupported.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary based on the clause inventory.
    input: >
      A list of structured sections (as returned by retrieve_policy).
    output: >
      A string representing the final summary. The summary must:
        - Include every clause from the inventory (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
        - Preserve all multiple approval conditions (especially for 5.2).
        - Contain no "scope bleed" or external assumptions.
        - Quote verbatim any clauses that cannot be safely summarized.
    error_handling: >
      If any of the 10 mandatory clauses are missing from the input sections,
      raise a validation error listing the missing clauses.
