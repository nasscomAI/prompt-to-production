# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for precise lookup.
    input: File paths to the policy documents (list of strings).
    output: A structured index mapping document names and section numbers to their exact text content.
    error_handling: If a document cannot be loaded, flag the missing document and proceed with the others.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: An employee question (string) and the indexed documents (dict).
    output: A string containing the compliant answer with citation, or the exact refusal template.
    error_handling: If a question is ambiguous, requires blending, or is not found, return the exact refusal template without hedging.
