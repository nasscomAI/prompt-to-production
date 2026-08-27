skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the three policy documents (List of Strings).
    output: A structured index or dictionary mapping document names and section numbers to their precise textual content.
    error_handling: Fails visibly if any of the three required policy documents are missing or malformed upon reading.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation OR the refusal template.
    input: The user's query (String) and the indexed documents object.
    output: A factual answer with source document name and section cited, OR the verbatim refusal template.
    error_handling: If the answer text requires combining segments from multiple documents or if it's missing entirely, reject generating a combined answer and output the exact refusal template instead.
