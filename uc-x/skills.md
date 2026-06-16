skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document filename and section number.
    input: Directory path or list of three file paths for the policy documents.
    output: Dict mapping filename → dict of section number → section text.
    error_handling: If any file cannot be read, exit with a clear error naming the missing file. If a file has no numbered sections, exit with an error stating the document structure was not recognised.

  - name: answer_question
    description: Searches the indexed documents for the question and returns a single-source answer with citation, or the exact refusal template if not found.
    input: Question string, indexed documents dict (output of retrieve_documents).
    output: Answer string — either a factual answer ending with [Source: filename, Section X.Y] from one document only, or the exact refusal template.
    error_handling: If the question matches content in more than one document, return only the most directly relevant single-source answer. Never merge content from two documents. If genuinely ambiguous across documents, use the refusal template.
