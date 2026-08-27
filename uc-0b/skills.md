skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns structured numbered sections for downstream summarization.
    input: "input_path: string file path to a UTF-8 .txt policy document containing numbered clauses."
    output: "object with full_text and sections[] where each section has clause_id (string like '2.3') and clause_text (string)."
    error_handling: "If file is missing, unreadable, empty, or unstructured, return a clear retrieval error and stop; do not fabricate missing clauses or inferred text."

  - name: summarize_policy
    description: Produces a compliant summary from structured sections while preserving all obligations and clause references.
    input: "sections object from retrieve_policy, including the 10 required clause IDs and their exact text."
    output: "summary text with clause-referenced lines that preserve binding verbs and all conditions without scope bleed."
    error_handling: "If any required clause is missing or a clause cannot be compressed safely, include the exact clause text verbatim and append [VERBATIM_REQUIRED]; if condition preservation is uncertain, do not soften and do not invent language outside source."
