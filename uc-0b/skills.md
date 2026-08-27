skills:
  - name: retrieve_policy
    description: Loads a plain text policy document and parses it into structured, numbered sections for accurate tracking and referencing.
    input: A string representing the absolute file path to the .txt policy document.
    output: A dictionary or list of structured sections, mapping clause numbers to their exact text.
    error_handling: If the file is unreadable or lacks clear numbered sections, return an error stating the document cannot be structured and refuse to proceed.

  - name: summarize_policy
    description: Takes the structured policy sections and generates a highly accurate summary that preserves all binding obligations and references clause numbers.
    input: The structured sections/dictionary output from retrieve_policy.
    output: A string containing the final compliant summary with explicit clause references, and verbatim quotes for complex clauses.
    error_handling: If the summary logic detects it cannot map every single clause without loss, it must output the problematic clause verbatim and flag it with '[VERBATIM]'. If input is invalid, it raises a validation error.
