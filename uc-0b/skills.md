skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered sections and individual clauses.
    input: String file_path (path to the source policy .txt file).
    output: List of dictionaries or structured objects containing section titles, clause identifiers (e.g., "1.1", "2.3"), and raw clause text.
    error_handling: Raises a FileNotFoundError or parsing error if the file is missing, empty, or unreadable, refusing to fabricate or guess unstated policy sections.

  - name: summarize_policy
    description: Takes structured policy sections and generates a faithful, clause-referenced summary that strictly preserves all multi-condition obligations, dual approvals, and binding verbs.
    input: Structured policy sections/clauses (from retrieve_policy) and string output_path (destination path for the summary text file).
    output: Summary text file written to output_path and/or string containing the structured summary with explicit clause citations.
    error_handling: Quotes clauses verbatim and flags them if they cannot be summarized without meaning loss or condition drop; refuses to interpolate external HR assumptions or unstated organizational rules.
