skills:
  - name: summarize_text
    description: Generates concise summary of the input text.
    input: Paragraph text.
    output: Short summary sentence.
    error_handling: If input too short return original text.

  - name: validate_summary
    description: Checks if summary preserves original meaning.
    input: Original text and summary.
    output: Validation result.
    error_handling: Return NEEDS_REVIEW if meaning changes.
