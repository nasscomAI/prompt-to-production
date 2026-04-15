# skills.md — UC-0A

skills:
  - name: classify_complaint
    description: Takes a single civic complaint row and returns its structured category, priority, reason, and flag using LLM classification with strict rule enforcement.
    input: A dictionary containing a single complaint row (keys like complaint_id, description, etc.)
    output: A dictionary object with strictly validated keys `category`, `priority`, `reason`, and `flag`.
    error_handling: If the LLM output is malformed, JSON parsing fails, or an API error occurs, returns category='Other' and flag='NEEDS_REVIEW' with a fallback reason.

  - name: batch_classify
    description: Reads the input CSV file, iterates through all rows calling classify_complaint, enforces additional programmatic fallbacks (e.g., severity keyword override), and writes all results to an output CSV file.
    input: input_path (string to input CSV), output_path (string to output CSV)
    output: None directly (writes a new CSV file to the output path)
    error_handling: Wraps individual row processing in a try/except so single failures don't crash the entire batch process.
