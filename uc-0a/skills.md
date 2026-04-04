skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason, and flag
      based on a fixed taxonomy and severity rules.
    input: >
      A dictionary representing a complaint row, containing at least a 'description'
      key with the complaint text.
    output:
      category: One of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
      priority: One of [Urgent, Standard, Low]
      reason: One sentence citing specific words from the description
      flag: 'NEEDS_REVIEW' or blank
    logic:
      - Normalize and analyze description text
      - Match keywords to allowed categories only
      - Detect severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
      - If any severity keyword present → set priority to Urgent
      - Otherwise assign Standard or Low based on context
      - Generate one-sentence reason referencing exact words from input
      - If no clear category match → assign category 'Other'
      - If ambiguity exists between multiple categories → set flag 'NEEDS_REVIEW'
    error_handling:
      - If description is missing, empty, or not a string:
          category: Other
          priority: Low
          reason: "Invalid input: missing or malformed description"
          flag: NEEDS_REVIEW
      - If multiple categories match with equal confidence:
          category: Other
          priority: Standard
          reason: "Ambiguous complaint with overlapping keywords"
          flag: NEEDS_REVIEW
      - If description is too vague to classify:
          category: Other
          priority: Low
          reason: "Insufficient detail in description"
          flag: NEEDS_REVIEW

  - name: batch_classify
    description: >
      Reads an input CSV file, applies classify_complaint to each row,
      and writes the enriched results to an output CSV file.
    input:
      input_csv_path: Path to input CSV file (string)
      output_csv_path: Path to output CSV file (string)
    output: >
      None (writes to file). The output CSV includes all original columns
      plus 'category', 'priority', 'reason', and 'flag'.
    processing_steps:
      - Load input CSV file
      - Iterate through each row
      - Validate presence of 'description' field
      - Apply classify_complaint to each valid row
      - Append classification results to row
      - Handle errors per row without stopping execution
      - Write all processed rows to output CSV
    error_handling:
      - If a row is missing 'description':
          - Assign:
              category: Other
              priority: Low
              reason: "Missing description field"
              flag: NEEDS_REVIEW
          - Continue processing remaining rows
      - If classify_complaint raises an exception:
          - Log the error
          - Assign fallback:
              category: Other
              priority: Low
              reason: "Processing error occurred"
              flag: NEEDS_REVIEW
      - Ensure output file is created even if some or all rows fail
      - Preserve row count consistency between input and output