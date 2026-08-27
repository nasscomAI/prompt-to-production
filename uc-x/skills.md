# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy baseline files, structurally indexing by document name and clause/section number.
    input: File paths to the 3 relevant policy TXT documents (HR, IT, Finance).
    output: Key-Value indexed database structure preserving document name and explicit section numbering links.
    error_handling: Critical halt and report system if any of the three inputs fail resolution. No partial loading permitted.

  - name: answer_question
    description: Searches indexed documents and strictly returns a single-source answer with citations or outputs the exact refusal template.
    input: User query string and structured text index from `retrieve_documents`.
    output: A single-document response string containing explicit citations (Document name + section) OR the exact unvaried refusal template string.
    error_handling: Unresolvable ambiguities mapping across multiple documents requiring blending must automatically trigger the explicit refusal template string.
