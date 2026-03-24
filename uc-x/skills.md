# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy text files, parses them into a section-indexed
      structure, and returns a lookup keyed by (document_name, section_number).
    input: >
      A list of file paths (strings) pointing to the three .txt policy files.
    output: >
      A dict mapping document filename → list of section dicts, each with keys:
      section_id (e.g. "3.1"), heading (if present), and text (full section
      content). Also returns a flat list of all (doc, section_id, text) tuples
      for search purposes.
    error_handling: >
      If any file is missing, raise FileNotFoundError naming the missing file —
      do not proceed with partial documents. If a file is empty or has no
      parseable sections, raise ValueError. Never silently skip a document.

  - name: answer_question
    description: >
      Searches the indexed documents for content relevant to the question and
      returns a single-source answer with citation, or the exact refusal
      template if no answer exists.
    input: >
      A question string and the indexed document structure returned by
      retrieve_documents.
    output: >
      A response string. If answerable: the answer text followed by a citation
      in the format [document_filename, Section X.Y]. If not answerable: the
      exact refusal template with no additions. Never returns a response without
      either a citation or the refusal template.
    error_handling: >
      If the question matches content in more than one document and a
      single-source answer is not sufficient, return the refusal template rather
      than blending sources. If the Claude API call fails, return a fallback
      message: "Unable to process question — please try again."