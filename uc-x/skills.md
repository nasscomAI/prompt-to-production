# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Load all UC-X policy documents and index them by document name and section number.
    input:
      type: object
      properties:
        paths:
          type: array
          items:
            type: string
      required: [paths]
    output:
      type: object
      description: Indexed policy contents as {document_name: {section: text}}.
    error_handling: "If any file is missing or unreadable, raise a clear error. If file format is invalid, return an explicit error message and do not proceed."

  - name: answer_question
    description: Search indexed policy documents and answer one question with a single-source citation or exact refusal.
    input:
      type: object
      properties:
        question:
          type: string
        index:
          type: object
      required: [question, index]
    output:
      type: object
      properties:
        answer:
          type: string
      required: [answer]
    error_handling: "If the question cannot be answered using one source policy and exact text, return the exact refusal template. If ambiguous across documents, return the refusal template. Do not hallucinate or provide partial guesses."
