# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and parses it into structured, numbered sections keyed by clause number.
    input: "policy_path (string): absolute or relative path to the policy text file (e.g. ../data/policy-documents/policy_hr_leave.txt)."
    output: "A dictionary mapping clause numbers (e.g. '2.3', '5.2', '7.2') to their full raw text content, preserving all binding verbs and conditions exactly as written."
    error_handling: "If the file does not exist, raises FileNotFoundError with the attempted path. If the file cannot be parsed into numbered sections (no clause numbers detected), raises ValueError describing the formatting issue."

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that references every clause number and preserves all obligations, conditions, and binding verbs.
    input: "Structured policy sections (dictionary mapping clause numbers to their raw text content) as returned by retrieve_policy."
    output: "A plain-text summary string with each clause summarized on its own line, prefixed by its clause number. Multi-condition clauses retain all conditions. Clauses that cannot be losslessly summarized are quoted verbatim with a [VERBATIM] flag."
    error_handling: "If any of the 10 required ground-truth clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing from the input, appends a [MISSING] warning for each absent clause to the output rather than silently omitting them."
