# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: answer_question
    description: Answers a user question by searching provided documents and extracting relevant information with citation.
    input: Question text (string), list of document file paths (list of strings).
    output: Answer text (string) with explicit citation of document and section.
    error_handling: If the answer cannot be found in the provided documents, returns a refusal message stating the answer is not available.

  - name: find_source_section
    description: Locates the section or clause in a document that contains the answer to a given question.
    input: Question text (string), document text (string).
    output: Section text (string) and section identifier (string or number).
    error_handling: If no relevant section is found, returns a message indicating no match found.
