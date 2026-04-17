skills:
  - name: classify_complaint
    description: >
      Maps a single citizen complaint to a structured classification. 
      Determines one of ten exact categories (Pothole, Flooding, etc.), 
      assigns priority (Urgent/Standard/Low) based on safety keywords, 
      and generates a one-sentence justification citing the original text.
    input: "Complaint description text (e.g., 'Large pothole near school')."
    input_format: String
    output: "A JSON object containing: category, priority, reason, and flag."
    output_format: Object { category: string, priority: string, reason: string, flag: string }
    error_handling: >
      If description is ambiguous, defaults category to 'Other' and flag to 'NEEDS_REVIEW'. 
      Strictly enforces 'Urgent' priority if keywords like 'injury', 'child', or 'hospital' appear.

  - name: batch_classify
    description: >
      Automates the end-to-end processing of a city's complaint CSV. 
      Reads from city-test-files, executes 'classify_complaint' for each record, 
      and saves the final results to a new results CSV file.
    input: "Path to input CSV (e.g., ../data/city-test-files/test_pune.csv)"
    input_format: File path (CSV)
    output: "Path to output CSV (e.g., uc-0a/results_pune.csv)"
    output_format: File path (CSV)
    error_handling: >
      Logs failed rows for manual inspection. Continues batch processing even 
      if individual rows trigger 'NEEDS_REVIEW' flags.
