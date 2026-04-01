# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: complaint_categorization
    description: Analyzes the citizen's text to map it to the most relevant municipal department.
    input: Raw text string containing the citizen's complaint description.
    output: A string representing one of the predefined categories (e.g., "Water Supply", "Road Infrastructure").
    error_handling: If the text is empty or lacks keywords related to the 6 main departments, return "Unclassified".

  - name: severity_assessment
    description: Evaluates the urgency of the complaint based on safety triggers and risk factors mentioned in the text.
    input: Raw text string from the complaint and the identified category.
    output: A single string representing the priority level: "High", "Medium", or "Low".
    error_handling: If no risk keywords (like 'danger', 'injury', or 'accident') are found, default the severity to "Low".

  - name: logic_extraction
    description: Extracts specific phrases or keywords from the input text to justify the categorization and severity.
    input: Raw text string from the complaint.
    output: A list of strings containing key phrases used for the final classification logic.
    error_handling: If no specific keywords are identified, return an empty list and flag the entry for manual review.