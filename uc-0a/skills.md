skills:
  - name: identify_complaint_category
    description: Analyzes municipal complaint descriptions to assign exactly one of ten predefined categories.
    input: Complaint description (String)
    output: Exact category string (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other)
    error_handling: Outputs "Other" and flags for human review if the description is ambiguous or does not fit predefined categories.

  - name: evaluate_severity_and_priority
    description: Scans descriptions for severity keywords (e.g., injury, child, hospital) to determine the classification priority level.
    input: Complaint description (String)
    output: Priority level string (Urgent, Standard, or Low)
    error_handling: Assigns "Standard" if no specific severity markers are detected.

  - name: extract_textual_evidence
    description: Cites specific words from the complaint description to provide a one-sentence justification for the classification.
    input: Complaint description (String) and classification results
    output: One-sentence reason string citing specific words verbatim.
    error_handling: Provides a generic "Classification based on overall description" sentence if specific citations fail.
