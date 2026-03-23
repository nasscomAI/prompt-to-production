# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and parses/indexes them explicitly by document name and section number.
    input: List of file paths to the three policy `.txt` files.
    output: A structured index or dictionary mapping `(Document Name, Section Number)` to the raw textual content of that section.
    error_handling: System fails and throws an error if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source factual answer with a citation, or the exact refusal template.
    input: The user's query string and the indexed structured documents from `retrieve_documents`.
    output: A string containing either the direct answer citing the `Document Name, Section Number` OR the exact verbatim refusal template.
    error_handling: REFUSES operation using the exact refusal template if the answer is completely missing, or if formulating an answer requires blending/merging information from two distinct documents.
