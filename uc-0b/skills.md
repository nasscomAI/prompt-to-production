# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Parses and structures the content of a municipal `.txt` policy document into individual numbered clauses, preserving their absolute original text.
    input: File path (string, e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: A dictionary mapping clause identifiers (e.g., "2.3") to the full literal text of that specific clause.
    error_handling: Handles missing files or unparseable formatting cleanly by returning specific error strings instead of crashing.

  - name: summarize_policy
    description: Generates a 1-1 condensed or verbatim mapped summary of the key obligations in a policy without dropping any specific conditions or scope constraints.
    input: A structured dictionary of clauses containing document policies.
    output: A rigorously validated summary text listing each identified clause.
    error_handling: Refuses to process and outputs a NEED_REVIEW fallback string if an input structure is corrupted or lacks identifiable obligations to summarize.
