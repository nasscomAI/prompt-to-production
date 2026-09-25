skills:
  - name: retrieve_policy
    description: Loads a plain text policy document and parses its content into structured numbered sections and individual numbered clauses.
    input: file_path (str, absolute or relative path to the source .txt policy document).
    output: Dict[str, Any] containing document metadata (title, doc_ref, version, effective_date) and a list of sections, where each section contains a section number, title, and a dictionary or list of numbered clauses with clause IDs (e.g., '2.3') and exact text.
    error_handling: If the file path does not exist, cannot be read, is empty, or does not contain recognizable numbered policy sections, raises FileNotFoundError or ValueError with a descriptive error message refusing execution rather than returning partial or speculative data.

  - name: summarize_policy
    description: Generates an obligation-preserving policy summary from structured sections, retaining every numbered clause, exact binding verbs, and multi-condition approvals while flagging verbatim clauses.
    input: structured_policy (Dict[str, Any] matching retrieve_policy output containing metadata, section headers, and numbered clauses).
    output: str containing formatted summary text organized by section with clause identifiers, preserving all binding requirements, multi-party conditions, and [VERBATIM] annotations without scope bleed.
    error_handling: Verifies that all numbered clauses from the source are present in the summary; checks for condition drop (such as single approver where dual approvers are mandated) or obligation softening; flags verbatim text with [VERBATIM] if condensation risks meaning loss; rejects insertion of external standard practice assumptions.
