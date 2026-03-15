# skills.md

skills:
  - name: extract_complaint_text
    description: Extracts and validates the complaint description from the incoming request.
    input: >
      JSON object containing a "description" field with the citizen complaint
      written in natural language.
    output: >
      Cleaned complaint text string with leading/trailing spaces removed and
      normalized for processing.
    error_handling: >
      If the description field is missing, empty, or not a string,
      return error: INVALID_INPUT and flag: NEEDS_REVIEW.

  - name: classify_complaint_category
    description: Determines the category of the complaint based on keywords and context.
    input: >
      Complaint description text string.
    output: >
      One category from the predefined list:
      Pothole, Flooding, Garbage, Streetlight, Water Leakage,
      Road Damage, Drainage Blockage, Other.
    error_handling: >
      If the complaint does not clearly match any category,
      return category: Other and flag: NEEDS_REVIEW.

  - name: determine_priority_level
    description: Assigns a priority level based on severity indicators in the complaint description.
    input: >
      Complaint description text string.
    output: >
      Priority value from the set:
      Low, Medium, High, Urgent.
    error_handling: >
      If severity cannot be determined from the description,
      default to Medium priority and flag: NEEDS_REVIEW.

  - name: generate_reason
    description: Generates a short explanation citing the words or phrases from the complaint description used for classification.
    input: >
      Complaint description text string along with selected category and priority.
    output: >
      A concise reason string referencing keywords or phrases found in the description.
    error_handling: >
      If no clear evidence can be extracted from the description,
      return reason: "Insufficient evidence in description" and flag: NEEDS_REVIEW.

  - name: format_classification_output
    description: Formats the classification result into a structured output object.
    input: >
      Category, priority, reason, and optional flag fields.
    output: >
      JSON object containing:
      {
        "category": string,
        "priority": string,
        "reason": string,
        "flag": optional string
      }
    error_handling: >
      If required fields are missing, return error: OUTPUT_FORMAT_ERROR
      and flag: NEEDS_REVIEW.