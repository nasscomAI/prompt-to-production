skills:
  - name: process_data
    description: Processes input text and generates cleaned output with basic metrics.
    input: A string containing input text data.
    output: A dictionary with processed text, metrics (word count), and optional flag.
    error_handling: If input is empty or invalid, returns empty result with word_count 0 and flag "NEEDS_REVIEW".

  - name: validate_input
    description: Validates input data before processing to ensure it meets requirements.
    input: A string containing raw input text.
    output: Boolean indicating validity and cleaned text.
    error_handling: If input is null or malformed, returns False and triggers "NEEDS_REVIEW" in processing.
