# skills.md — UC-X Policy Document Q&A System

skills:
  - name: load_policy_documents
    description: Loads all three policy documents and indexes them by document name and section number for retrieval.
    input: List of file paths (strings) to the three policy documents.
    output: Dictionary mapping document names to structured content with section numbers as keys and section text as values.
    error_handling: If any file cannot be read or parsed, raise an error with the specific filename. Do not proceed with partial data.

  - name: search_policy_content
    description: Searches indexed policy documents for content relevant to a user question and identifies the most relevant single document and section.
    input: User question (string) and indexed policy documents (dictionary from load_policy_documents).
    output: Tuple of (document_name, section_number, section_text) for the most relevant match, or None if no relevant content found.
    error_handling: Returns None if the question cannot be matched to any document section. Never returns multiple documents or blended results.

  - name: format_answer
    description: Formats the retrieved policy section into a user-friendly answer with proper citation.
    input: Document name (string), section number (string), section text (string), and original user question (string).
    output: Formatted answer string with citation in the format "According to [document_name] section [section_number]: [answer text]"
    error_handling: If any input is None or empty, returns the refusal template instead of attempting to construct an answer.

  - name: apply_refusal_template
    description: Returns the exact refusal message when a question is not covered in the policy documents.
    input: None (this is called when no relevant policy content is found).
    output: String containing the exact refusal template message.
    error_handling: This skill has no error condition - it always returns the template verbatim.

  - name: validate_single_source
    description: Validates that an answer comes from exactly one document and section, not a blend of multiple sources.
    input: Document name (string), section number (string), and answer text (string).
    output: Boolean indicating whether the answer is from a single source.
    error_handling: Returns False if multiple document references are detected or if hedging phrases are present.
