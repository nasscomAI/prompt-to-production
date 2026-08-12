# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by section number and document name.
    input: Paths to the HR, IT, and finance policy text files.
    output: Dictionary mapping document names to dictionaries of section numbers and section text.
    error_handling: Raises a clear error if any document is missing or cannot be parsed into numbered sections.

  - name: answer_question
    description: Find a single-source answer for a policy question or return a clean refusal when the question is not covered.
    input: A natural language question and the indexed policy documents.
    output: A string answer with a source citation, or the exact refusal template.
    error_handling: If the question is ambiguous across multiple documents, return the refusal template exactly.
