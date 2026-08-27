skills:
  - name: read_file
    description: Reads the input policy document from a file
    input: File path (string)
    output: File content (string)
    error_handling: Returns error message if file cannot be read

  - name: summarize_text
    description: Generates a concise summary of the policy document
    input: Raw text (string)
    output: Summary text (string)
    error_handling: Returns original text if input is empty or invalid