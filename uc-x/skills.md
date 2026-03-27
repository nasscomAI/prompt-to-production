# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_document
    description: Loads a specified policy document and returns its content as structured sections.
    input: Path to a .txt policy file.
    output: List of dictionaries, each with 'section', 'text', and optionally 'clause'.
    error_handling: Raises an error if the file is missing or cannot be parsed.

  - name: answer_question
    description: Answers a user question using only the content of a single policy document, citing document and clause if present, or returning the refusal template if not covered.
    input: Question string and list of document sections.
    output: String containing the answer, with document and clause reference, or the refusal template verbatim.
    error_handling: If the answer is not found in any document, returns the refusal template exactly as specified.
