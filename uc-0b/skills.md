skills:
  - name: retrieve_policy
    description: Ingests a raw policy text file and parses it into structured sections and individual numbered clauses.
    input: file_path (str - path to the .txt policy document)
    output: dict containing document title, reference, version, and structured dictionary of sections mapped to numbered clauses
    error_handling: Handles missing files and encoding issues safely; flags unparsed or irregular lines.

  - name: summarize_policy
    description: Generates a rigorous, structured policy summary from parsed policy clauses preserving all conditions, approvals, deadlines, and binding verbs with clause citations.
    input: policy_data (dict containing structured policy metadata, sections, and clauses)
    output: summary_text (str - formatted summary containing all clause obligations and citations)
    error_handling: Verifies presence of all numbered clauses; quotes verbatim any clause where compression risks meaning loss.

