# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: Complaint Classifier
    description: Analyzes the complaints mentioned in the dataset and classifies them into categories and priorities.
    input: Complaints in the form of text or images.
    output: Category(Roads,Health,Education)
    error_handling: If text is unclear, assign category as "Other"

  - name: Priority Detection
    description: Assigns priority level based on urgency keywords in complaint.
    input: Complaint text (string)
    output: Priority (High, Medium, Low)
    error_handling: If no urgency keywords found, assign "Medium"
