# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Triages a single citizen complaint description into category and priority according to the taxonomy.
    input: String containing the citizen's complaint description.
    output: A classification object containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Assigns 'Other' category and 'NEEDS_REVIEW' flag for ambiguous or undefined complaints.

  - name: batch_classify
    description: Reads an input CSV of complaints and writes a classified CSV output for a specific city.
    input: Input CSV file path and target output CSV file path.
    output: A CSV file containing classified rows with all required taxonomy fields.
    error_handling: Handles missing data by applying the 'Other' category and ensuring the 'flag' field is set for review.
