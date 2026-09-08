skills:
  - name: classify_complaint
    description: Classifies a single complaint record into an allowed category, determines priority based on safety keywords, generates an evidence-based reason citing description text, and flags ambiguous records.
    input: Dictionary representing a complaint row with keys 'complaint_id', 'description', 'location', 'ward', and other metadata fields.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag', preserving existing row attributes.
    error_handling: When description is missing, malformed, or ambiguous across categories, sets flag to 'NEEDS_REVIEW' and category to 'Other' or best fit without crashing.

  - name: batch_classify
    description: Reads a city complaint CSV file, applies classify_complaint to each row sequentially, and writes the structured classification results to an output CSV file.
    input: File path strings for input CSV (test city data) and output CSV destination.
    output: Destination CSV file populated with classified rows including category, priority, reason, and flag columns.
    error_handling: Handles missing rows, empty descriptions, or unexpected CSV encodings gracefully by logging an error, assigning 'NEEDS_REVIEW', and continuing batch processing.
