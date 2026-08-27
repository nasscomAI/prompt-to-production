# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: document_reader
    description: Reads text from a document.
    input: File path.
    output: Document text.
    error_handling: Shows error if file not found.

  - name: question_answering
    description: Finds answer to a question from document.
    input: Question and document text.
    output: Answer string.
    error_handling: Returns "Not found" if answer missing.

  - name: output_writer
    description: Writes answer to file.
    input: Answer text.
    output: Output file.
    error_handling: Shows error if writing fails.