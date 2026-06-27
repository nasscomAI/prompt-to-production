skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files (HR leave, IT acceptable use, Finance
      reimbursement), parses them into numbered sections and clauses, and indexes
      by document filename and section number for lookup.
    input: List of file paths (strings) to the three policy .txt files.
    output: Dict mapping document filenames to lists of section objects, each
      with header and clause list.
    error_handling: >
      If any file does not exist, raise FileNotFoundError with the missing path.
      If a file contains no numbered sections, log a warning and skip it.

  - name: answer_question
    description: >
      Takes a user question string and the document index, matches the question
      to the most relevant policy section across documents, and returns a single-
      source answer with citation. Uses the refusal template if no match found.
    input: Question string, document index dict.
    output: Answer string with source citation, or the refusal template.
    error_handling: >
      If the question matches sections in multiple documents with equal relevance,
      pick the most specific match and answer from that single document only.
      Never blend. If relevance score is below threshold, return refusal template.
