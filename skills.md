# skills.md

skills:
  - name: classify_complaint
    description: Analyzes the text of a civic complaint and categorizes it into a standard city department.
    input: String containing the description of the complaint.
    output: String representing the assigned category (e.g., "Roads & Traffic", "Sanitation", etc.).
    error_handling: Returns "Uncategorized" if the input text is ambiguous, too short, or lacks recognizable civic keywords.

  - name: extract_location
    description: Extracts the specific neighborhood, street, or landmark mentioned in the complaint.
    input: String containing the full complaint text and context provided by the citizen.
    output: String representing the extracted location, or "Unknown" if not specified.
    error_handling: Returns "Unknown" if no identifiable location can be parsed from the text.
    
  - name: assess_risk_level
    description: Evaluates the severity and urgency of the complaint based on keywords relating to safety or public health.
    input: String containing the description of the complaint.
    output: String representing the risk level, strictly one of "High", "Medium", or "Low".
    error_handling: Defaults to "Medium" risk if the urgency is unclear or cannot be reliably determined.
