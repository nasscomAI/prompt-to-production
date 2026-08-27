skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint description into the approved civic issue
      category and assigns a priority level with justification.
    input: >
      A single complaint row containing:
      {
        "id": string,
        "description": string
      }
    output: >
      Structured classification result:
      {
        "category": "Pothole | Flooding | Streetlight | Waste | Noise | Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other",
        "priority": "Urgent | Standard | Low",
        "reason": "One sentence citing specific words from the description",
        "flag": "NEEDS_REVIEW or blank"
      }
    error_handling: >
      If description is empty or cannot be interpreted, return category as
      Other, priority as Standard, reason explaining insufficient
      information, and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads a CSV file containing complaint descriptions, applies the
      classify_complaint skill to each row, and writes the structured results
      to an output CSV file.
    input: >
      Input CSV file path containing complaint rows with descriptions.
    output: >
      Output CSV file containing classification results for each complaint
      including category, priority, reason, and flag.
    error_handling: >
      If the input CSV is missing required columns or cannot be parsed,
      return an error indicating invalid input format.
