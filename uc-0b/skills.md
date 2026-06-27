# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Reads the raw text of the policy document from the file system.
    input: file_path (str) - The path to the policy .txt file.
    output: content (str) - The raw text content of the policy document.
    error_handling: If the file is not found or cannot be read, return an error message indicating the failure to retrieve the policy.

  - name: summarize_policy
    description: Parses the policy text and generates a strict, compliant summary of required clauses, ensuring no dropped conditions or scope bleed.
    input: content (str) - The raw text of the policy document.
    output: summary (str) - A formatted string containing the required clauses summarized or quoted exactly.
    error_handling: If the text is empty or missing expected sections, output a warning that the policy text is malformed.
