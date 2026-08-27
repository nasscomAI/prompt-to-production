# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy text files from disk and parses them into a structured index mapped by document filename and section numbers.
    input: None.
    output: A dictionary representing the indexed policy sections, mapping (filename, section_number) to section text.
    error_handling: If any of the three policy files are missing or unreadable, raises FileNotFoundError.

  - name: answer_question
    description: Searches the indexed policy documents for relevant sections, answers user questions using single-source information, and includes file and section number citations.
    input: Question (string) and indexed documents (as returned by retrieve_documents).
    output: A string containing the single-source answer with proper section and document name citations, or the exact refusal template if the answer is not present.
    error_handling: If the query is ambiguous, references multiple conflicting documents, or is not answered in the files, returns the verbatim refusal template.
