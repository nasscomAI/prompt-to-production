skills:
  - name: retrieve_documents
    description: Load all three policy .txt files, parse them into structured sections indexed by document name and section number.
    input: A list of file paths to the three policy .txt documents.
    output: A dictionary keyed by document filename, where each value is a list of sections with keys: section_number, heading, body.
    error_handling: If any file is missing or unreadable, raise a clear error listing the missing file path. If a file has no numbered sections, index its full content under section_number "0".

  - name: answer_question
    description: Search the indexed policy documents for the user's question and return either a single-source answer with citation or the refusal template.
    input: A user question string, and the indexed document dictionary from retrieve_documents.
    output: A single string — either the answer with source citation (document name + section number), or the verbatim refusal template if the question is not covered.
    error_handling: If the question matches content in more than one document, return the answer from the most relevant single document only — never blend. If no match is found in any document, return the refusal template exactly.
