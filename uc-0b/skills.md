skills:
  - name: retrieve_policy
    description: Ingests a raw policy text file and parses it into structured sections and numbered clause blocks with associated metadata.
    input: File path (str) pointing to a plain text (.txt) policy document.
    output: A structured dictionary mapping document metadata (title, reference, version) and sections (section title, list of clauses with clause ID and verbatim text).
    error_handling: Raises FileNotFoundError if the file cannot be found. Raises ValueError if the document is empty or lacks expected numbered clause patterns.

  - name: summarize_policy
    description: Takes structured policy sections, applies RICE enforcement rules to verify that obligations, binding verbs, and multi-condition approvals are fully preserved, and renders an auditable summary with explicit clause numbers.
    input: Structured policy sections dictionary produced by retrieve_policy.
    output: Formatted summary text (str) with clause citations, preserving all binding verbs and dual-approval requirements.
    error_handling: Raises AssertionError if any numbered clause from the source is omitted, if binding modal verbs are altered, or if multi-party approval requirements (e.g., Clause 5.2) are dropped.
