# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: High-fidelity classification of a single citizen complaint string into a strictly validated JSON schema, enforcing categorical taxonomy and deterministic severity escalation.
    input: 
      type: dict
      schema: { "description": "string" }
      requirement: Raw citizen input from the 'description' field only.
    output:
      type: dict
      schema: { "category": "string", "priority": "string", "reason": "string", "flag": "string" }
      validation:
        category: Must match exactly one from: [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
        priority: One of: [Urgent, Standard, Low].
        reason: Exactly one sentence citing raw text from the description in quotes.
        flag: "NEEDS_REVIEW" if ambiguous, otherwise empty string.
    error_handling: Trigger 'Other' and 'NEEDS_REVIEW' for any input that is ambiguous, nonsensical, or lacks sufficient detail for confident classification.

  - name: batch_classify
    description: Automated batch processing pipeline that reads city-specific test files and generates standardized classification output files.
    input:
      fields:
        input_file: "../data/city-test-files/test_[city].csv"
        output_file: "uc-0a/results_[city].csv"
      requirement: Processes exactly 1 row at a time using classify_complaint logic.
    output:
      type: csv_file
      convention: results_[city].csv containing category, priority, reason, and flag columns.
    error_handling: Report file access errors; for individual row failures, log the exception and assign the 'NEEDS_REVIEW' flag to the specific row in the output file to ensure batch continuation.
