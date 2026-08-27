# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: retrieve_documents
    description: >
      Loads all three policy documents and indexes them by document name
      and section number for lookup.
    input: >
      Paths to policy text files.
    output: >
      Dictionary mapping document names to section-numbered text blocks.
    error_handling: >
      If a document cannot be read, return NEEDS_REVIEW.

  - name: answer_question
    description: >
      Searches the indexed documents for a matching policy clause and
      returns the answer with citation.
    input: >
      Question text and indexed policy documents.
    output: >
      Answer string containing the policy statement and citation.
    error_handling: >
      If no matching section is found, return the refusal template.
