skills:
  - name: retrieve_policy
    description: Ingests a plain-text policy document and parses it into structured document metadata, sections, and individual numbered clauses.
    input: file_path (str) path to the policy text file.
    output: dict containing metadata (title, reference, version, effective date), list of sections, and a complete inventory of structured clause dictionaries with clause_id, section_name, and clause_text.
    error_handling: Handles missing files, unreadable encodings, and empty documents by returning an error structure and raising clear descriptive errors without crashing unhandled.

  - name: summarize_policy
    description: Transforms structured policy data into an executive, clause-referenced summary that strictly preserves all binding verbs, approvers, conditions, and numerical thresholds.
    input: dict output from retrieve_policy containing structured sections and clauses.
    output: str formatted plain text summary with full clause references, preserved binding obligations, and an explicit clause coverage inventory.
    error_handling: Verifies that 100% of parsed numbered clauses are represented in the final summary; quotes complex clauses verbatim if condensing risks meaning loss.
