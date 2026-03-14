skills:
  - name: retrieve_policy
    description: Opens and loads the raw .txt policy file and segments it into structured sections and numbered clauses for accurate referencing.
    input: File path (string) to the policy document text file.
    output: A dictionary or List[Dictionary] structure containing the parsed sections mapped by clause number and string content.
    error_handling: Raises an IOError if the file is missing or corrupted; flags any section that doesn't follow standard numbering conventions.

  - name: summarize_policy
    description: Processes the structured policy text to generate a compliant summary ensuring no condition dropping and no scope bleed.
    input: Structured policy sections (parsed from retrieve_policy).
    output: A single formatted text string containing the summarized policy highlighting all required conditions and retaining exact clause citations.
    error_handling: Quotes any clause verbatim and flags it in output if its conditions are too complex to safely summarize algorithmically.
