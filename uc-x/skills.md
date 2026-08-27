# skills.md

skills:
  - name: retrieve_documents
    description: Opens the document directory, mapping each line to its explicit policy document and section index number to avoid bleed.
    input: Filenames of the acceptable policy texts.
    output: A vectorized or indexed structured database associating text fragments strictly to their filenames and section bounds.
    error_handling: Systematically blocks execution and reports an explicit error context if files cannot be found or read contextually.

  - name: answer_question
    description: Processes a user's prompt entirely linearly against individual documents, generating a cited response strictly from one isolated document source.
    input: The indexed database and the user's natural language question.
    output: A rigorously formatted response quoting a single factual source paired with a citation metric [Filename, Section X.Y].
    error_handling: Maps out of scope, conflicting, or unanswerable requests strictly back to the verbatim refusal template without any hedging language.
