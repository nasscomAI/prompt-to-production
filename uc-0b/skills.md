skills:
  - name: retrieve_policy
    description: Ingests a plain text municipal policy document and parses it into structured sections and numbered clauses with metadata.
    input: input_path (str) representing the absolute or relative file path to the source policy .txt file.
    output: A structured dictionary containing document metadata (title, version, document reference) and an ordered list of sections with individual numbered clauses.
    error_handling: Handles missing, empty, or unreadable policy files gracefully by raising or returning structured error states.

  - name: summarize_policy
    description: Generates a high-fidelity, compliance-audited policy summary from structured policy sections preserving every numbered clause, multi-condition approval, and binding verb.
    input: Structured policy dictionary or list of section objects produced by retrieve_policy.
    output: Formatted summary string containing executive highlights, section breakdowns with full clause fidelity, and compliance verification notes.
    error_handling: Verifies complete clause coverage across all input sections, preventing omission, condition dropping, or scope bleed.
