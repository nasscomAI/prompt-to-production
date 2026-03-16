skills:
  - name: extract_numbers
    description: Detects numeric values present in text.
    input: Text containing numbers.
    output: List of numbers.
    error_handling: Return empty list if none found.

  - name: validate_numbers
    description: Verifies extracted numbers against source text.
    input: Source text and extracted numbers.
    output: Verified numbers.
    error_handling: Return NEEDS_REVIEW if mismatch occurs.
