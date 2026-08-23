# skills.md — UC-X Ask My Documents Skills

skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files (HR, IT, Finance) from data/policy-documents/, parses them into structured sections, and indexes content by document name and section number.
    input: data_dir (str path to policy documents directory).
    output: Dict mapping document names to section numbers and text snippets.
    error_handling: Raises FileNotFoundError if any policy document is missing.

  - name: answer_question
    description: Processes a user query against indexed policy documents, matches relevant sections using single-source attribution, and returns either a cited answer or the exact refusal template.
    input: query (str user question), indexed_docs (dict).
    output: String response containing single-source answer + citation OR verbatim refusal template.
    error_handling: Triggers refusal template if query cannot be unambiguously answered from a single document.
