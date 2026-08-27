# skills.md

skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts content as structured numbered sections.
    input: Path to a .txt policy file.
    output: A list of dictionaries, each containing a clause number and its text.
    error_handling: If the file is not found or empty, raise an error or return an empty list.

  - name: summarize_policy
    description: Summarizes structured policy sections into a compliant summary with clause references.
    input: A list of structured policy sections.
    output: A string containing the compliant summary.
    error_handling: If a section cannot be summarized accurately, quote it verbatim.
