# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to policy documents.
    output: A structured index mapping document names and section numbers to their text.
    error_handling: Return an error if any file cannot be read.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or outputs the strict refusal template if the answer is missing or ambiguous.
    input: The indexed documents and a user's question string.
    output: The extracted answer with a citation, or the verbatim refusal template.
    error_handling: Automatically trigger the strict refusal template if multiple contradictory or blending sources are required, or if no source matches.
