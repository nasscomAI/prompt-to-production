skills:
  - name: retrieve_policy
    description: Loads a raw policy text file and parses it into structured numbered sections for precise extraction.
    input: file_path (str path to policy text document)
    output: A dictionary mapping clause/section numbers to their raw text content.
    error_handling: Raises FileNotFoundError if file is missing, and returns empty structure on empty files.

  - name: summarize_policy
    description: Takes the structured policy sections and generates a summary that preserves binding verbs, multi-conditions, and clause numbers verbatim where necessary to avoid meaning loss.
    input: structured_sections (dict of clause content)
    output: A structured text summary of the policy.
    error_handling: Flags sections that are missing or fail matching criteria as needing manual review.
