# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single unstructured citizen complaint string and categorizes it based on the strict civic taxonomy.
    input: A single string of raw unstructured text representing a civic complaint.
    output: A structured dictionary/object containing exactly four fields - category (string), priority (string), reason (string), and flag (string).
    error_handling: If the complaint cannot be confidently assigned a taxonomy category from the explicit list based on the input text, it will set the flag to "NEEDS_REVIEW" and default category to "Other".

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV source by applying the classify_complaint skill to each row.
    input: A file path or data structure representing the input CSV file containing raw complaint descriptions.
    output: An exported CSV file or table structure combining original rows with the new predicted category, priority, reason, and flag columns.
    error_handling: Ignores malformed/empty rows, gracefully handling file I/O errors and saving partially generated outputs on fatal errors.
