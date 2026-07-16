# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: Paths to the three policy .txt files.
    output: >
      An ordered list of {doc_name, clause_number, clause_text} entries
      covering every numbered clause across all three documents.
    error_handling: >
      If any of the three files is missing or unreadable, raise a clear
      error naming the missing file rather than answering from a partial
      index silently.

  - name: answer_question
    description: Searches the indexed documents for the single best-matching section and returns a cited answer or the exact refusal template.
    input: A natural-language question string, plus the index from retrieve_documents.
    output: >
      Either {answer, doc_name, clause_number} citing exactly one section,
      or the exact refusal template string when no section clearly answers
      the question.
    error_handling: >
      If the best-matching sections come from more than one document with
      comparable relevance, still returns only the single top-scoring
      section — never blends wording from two documents into one answer.
      If no section clears the minimum relevance threshold, returns the
      refusal template verbatim rather than a hedged guess.
