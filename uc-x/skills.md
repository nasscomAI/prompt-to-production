# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# UC-X — Skills

## retrieve_documents
- Loads all three policy files.
- Indexes by document name and section number.

## answer_question
- Searches indexed documents.
- Returns single-source answer with citation or refusal template.

skills:
  - name: [skill_name]
    description: [One sentence — what does this skill do?]
    input: [What does it receive? Type and format.]
    output: [What does it return? Type and format.]
    error_handling: [What does it do when input is invalid or ambiguous?]

  - name: [second_skill_name]
    description: [One sentence]
    input: [Type and format]
    output: [Type and format]
    error_handling: [What does it do when input is invalid or ambiguous?]
