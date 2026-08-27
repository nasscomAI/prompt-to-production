# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint_category
    description: Determines the civic issue category based on keywords in the complaint description.
    input: 
      Complaint description text (string) from the CSV dataset.
    output: 
      A single category label from the allowed list: 
      Sanitation, Water, Roads, Electricity, Public Safety, Other.
    error_handling: 
      If no keywords match any known category, return category "Other" 
      and flag the complaint for manual review.

  - name: determine_severity
    description: Assigns a severity level based on risk and urgency indicators in the complaint.
    input: 
      Complaint description text (string).
    output: 
      Severity level: Urgent, Medium, or Low.
    error_handling: 
      If severity indicators are unclear, default to Medium 
      and include a note in the reason field explaining the ambiguity.