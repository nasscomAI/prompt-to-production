# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: summarize_policy
    description: Summarizes a given policy document into a short and clear summary.
    input: text,paragraph or document content
    output: Summary of the document in text form.
    error_handling:  - If input is empty → return "No content to summarize"
      - If input is unclear → return "Unable to summarize"
      - If input is too short → return "Insufficient content"

  - name: summarize_policy
    description: Summarizes a given policy document into a short and clear summary.
    input: text, paragraph or document content
    output: text, 3–5 line summary covering key points
    error_handling:  - If input is empty → return "No content to summarize"
      - If input is unclear → return "Unable to summarize"
      - If input is too short → return "Insufficient content"
