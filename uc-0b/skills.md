# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy document from a text file and returns its content as structured numbered sections with preserved formatting.
    input: File path (string) pointing to a .txt policy document with numbered clause structure.
    output: Dictionary with keys 'raw_text' (full document string), 'clauses' (list of tuples containing clause_number and clause_text), and 'metadata' (document header information if present).
    error_handling: Returns None with error message if file does not exist, cannot be read, or does not contain recognizable numbered clause structure. Raises ValueError if file path is empty or invalid type.

  - name: summarize_policy
    description: Produces a compliance-preserving summary of policy clauses with mandatory clause references and obligation preservation.
    input: Dictionary from retrieve_policy containing 'clauses' (list of clause tuples) and 'metadata' (document info).
    output: String containing formatted summary where each statement includes clause reference in brackets [X.Y], preserves all binding verbs and multi-condition requirements, and flags verbatim quotes with [VERBATIM] tag when condensation would lose meaning.
    error_handling: Returns error string prefixed with "ERROR:" if input structure is invalid, clauses list is empty, or if critical clause parsing fails. Refuses to summarize and returns "AMBIGUOUS SOURCE" if clause numbering is inconsistent or duplicated.
