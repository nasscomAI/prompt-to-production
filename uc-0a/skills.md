# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint record to determine its category, priority, reason, and review flag according to municipal classification rules and enforcement constraints.
    input:
      type: dictionary / record
      description: A single complaint record containing municipal grievance details.
      fields:
        complaint_id: string
        date_raised: string
        city: string
        ward: string
        location: string
        description: string
        reported_by: string
        days_open: integer or string
    output:
      type: dictionary / record
      description: The classification results adhering strictly to the schema constraints.
      fields:
        category: string (Must be strictly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
        priority: string (Must be strictly one of: Urgent, Standard, Low; Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
        reason: string (Exactly one sentence explicitly citing verbatim words from description as evidence)
        flag: string ("NEEDS_REVIEW" if ambiguous or multi-category; otherwise "")
    enforcement_rules_followed:
      - CATEGORY_ENUM: Restricts category output strictly to the 10 allowed exact strings.
      - PRIORITY_ENUM: Restricts priority output strictly to Urgent, Standard, or Low.
      - SEVERITY_TRIGGER_URGENT: Deterministically assigns Urgent if any of the 9 defined severity keywords appear in description (case-insensitively).
      - REASON_SENTENCE_AND_EVIDENCE: Produces exactly one sentence citing specific verbatim words from the complaint text.
      - FLAG_ENUM_AND_AMBIGUITY: Sets flag to "NEEDS_REVIEW" only when genuinely ambiguous or two categories are equally plausible; otherwise sets empty string ("").
      - REFUSAL_AND_FALLBACK: Sets category to "Other" and flag to "NEEDS_REVIEW" for indecipherable or unclassifiable text.
      - OUTPUT_FIELDS_SCHEMA: Guarantees that all four output fields are returned.
    error_handling: >
      "Unable to classify because the complaint description is missing or invalid." If a complaint touches multiple categories without a single clear primary domain, assign the most plausible category and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, iteratively executes classify_complaint on every record, and writes the augmented records with classification fields to an output results CSV file.
    input:
      type: file path / string
      description: Path to the input CSV file containing citizen complaint records without classification columns.
      format: CSV with headers (complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output:
      type: file path / string
      description: Path to the output results CSV file containing all original columns plus the four classification columns.
      format: CSV with headers (complaint_id, date_raised, city, ward, location, description, reported_by, days_open, category, priority, reason, flag)
    enforcement_rules_followed:
      - OUTPUT_FIELDS_SCHEMA: Appends all four required classification columns (category, priority, reason, flag) to every row.
      - RECORD_INTEGRITY: Preserves the exact row count, row order, and original input field values from the source CSV.
      - DETERMINISTIC_EXECUTION: Applies classify_complaint uniformly across all rows to prevent taxonomy drift and unvalidated entries.
    error_handling: >
      If the input CSV file is missing, empty, or cannot be opened, raise a FileNotFoundError with a clear error message. If a required input column is missing, raise a ValueError specifying the missing header. If an error occurs while classifying an individual row, populate the row with fallback values (category: "Other", priority: "Standard", reason: "Processing error encountered on row.", flag: "NEEDS_REVIEW") to ensure the batch run completes.
