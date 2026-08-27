# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Indexes and searches across the 3 policy documents (HR, IT, Finance) by section numbers and key policy terms.
    input: query string or question
    output: relevant document sections with exact file names and section identifiers
    error_handling: Returns empty result set if query does not match document contents.

  - name: answer_question
    description: Evaluates retrieved sections and formulates a single-source answer with citations or emits the refusal template.
    input: question (str), retrieved document sections
    output: answer string with source citation OR exact refusal template
    error_handling: Triggers refusal template if multiple documents conflict or topic is absent.
