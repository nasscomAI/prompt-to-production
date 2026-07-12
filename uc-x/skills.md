skills:
  - name: retrieve_documents
    description: >
      Loads all three policy text files (HR, IT, Finance) and indexes them
      by document name and section number for efficient lookup.
    input: >
      directory_path (string): path to the directory containing the three
      policy .txt files.
    output: >
      A dict with keys being document short names ("HR", "IT", "Finance")
      and values being dicts of {section_id: section_text} where section_id
      is like "2.6" or "3.1" and section_text is the full clause text.
    error_handling: >
      If any of the three files is missing, raise FileNotFoundError with
      the filename. If a file cannot be parsed into sections, skip it and
      print a warning to stderr.

  - name: answer_question
    description: >
      Takes an indexed document store and a user question, finds the most
      relevant single-source section, and returns an answer with citation
      or the refusal template if no match exists.
    input: >
      documents (dict): output from retrieve_documents. question (string):
      the user's natural language question.
    output: >
      A dict with keys: answer (string, the response text), source (string,
      document name and section number, or "none"), used_refusal (boolean,
      true if refusal template was used).
    error_handling: >
      If the question matches sections from multiple documents, answer from
      only the most relevant one and do not blend. If no section matches,
      return the refusal template exactly.
