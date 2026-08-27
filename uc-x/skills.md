skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes their content by document name and section number, ready for lookup.
    input: A list of file paths to the three policy documents.
    output: A nested dictionary keyed by document filename, then by section number (e.g. "3.1"), containing the section text as a string.
    error_handling: If any file is missing, report the missing file and continue loading the others. If a file cannot be parsed into sections, store its full text under key "UNPARSED" and continue.

  - name: answer_question
    description: Searches the indexed documents for the user's question and returns a single-source answer with citation, or the exact refusal template if no single document can answer it.
    input: A user question string and the indexed document dictionary from retrieve_documents.
    output: A string answer in the format 'Answer: [answer text] [Source: document_name, section X.X]', or the exact refusal template if the question is not covered or requires cross-document blending.
    error_handling: If matching sections are found in more than one document and the question requires combining them, do not blend — output the refusal template. Never use hedging language. If keyword matching finds no relevant section, output the refusal template exactly.
