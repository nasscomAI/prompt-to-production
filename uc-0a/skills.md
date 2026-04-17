# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single raw citizen complaint text to determine its maintenance category and safety priority, providing a cited reason for the decision.
    input: 
      type: object
      properties:
        description: 
          type: string
          description: "The raw text of the citizen complaint (e.g., 'Large pothole near school')."
    output:
      type: object
      properties:
        category:
          type: string
          enum: [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
        priority:
          type: string
          enum: [Urgent, Standard, Low]
        reason:
          type: string
          description: "A single sentence citing specific evidence from the input description."
        flag:
          type: string
          description: "Set to 'NEEDS_REVIEW' if ambiguity is detected; otherwise empty."
    error_handling:
      - scenario: "Input description is missing or empty"
        action: "Return category: 'Other', priority: 'Low', reason: 'Missing input description', flag: 'NEEDS_REVIEW'"
      - scenario: "Input is genuinely ambiguous (e.g., 'it is broken')"
        action: "Return category: 'Other', flag: 'NEEDS_REVIEW' and cite the lack of detail in reason"
      - scenario: "Multiple potential categories detected"
        action: "Select the most severe maintenance category and note the ambiguity in the flag field"

  - name: batch_classify
    description: Orchestrates the end-to-end classification workflow by reading a batch of complaints from a CSV and writing results to a new file.
    input:
      type: object
      properties:
        input_file:
          type: string
          description: "Path to the input CSV file containing raw complaints."
        output_file:
          type: string
          description: "Path where the results CSV (with added classification columns) should be saved."
    output:
      type: object
      properties:
        rows_processed: 
          type: integer
        status: 
          type: string
    error_handling:
      - scenario: "Input file not found or inaccessible"
        action: "Raise informative error and terminate process before writing"
      - scenario: "Source row missing a description column"
        action: "Skip the row, log a warning, and continue to ensure batch completion"
      - scenario: "Permission denied on output path"
        action: "Attempt to write to a temporary fallback location or fail with clear permission error"

  - name: detect_severity
    description: "Granular check for safety-critical keywords to ensure mandatory escalation."
    input:
      type: string
      description: "Complaint description string."
    output:
      type: boolean
      description: "Returns true if any urgent keywords (injury, child, school, hospital, etc.) are present."
    error_handling:
      - scenario: "Keyword is found within another word (e.g., 'schooling')"
        action: "Use regex boundaries to ensure only exact keyword matches trigger escalation."
