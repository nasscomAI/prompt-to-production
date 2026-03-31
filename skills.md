# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: "File path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)."
    output: "Structured list of numbered sections, each containing the clause number, heading (if any), and full clause text."
    error_handling: "If the file path is invalid, the file is empty, or the file is not a readable .txt document, return an error message and do not attempt to fabricate content."

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: "Structured numbered sections as returned by retrieve_policy."
    output: "A plain-text summary where each clause is referenced by number, binding verbs are preserved exactly, multi-condition obligations retain all conditions, and any clause that cannot be summarised without meaning loss is quoted verbatim with a [VERBATIM] flag."
    error_handling: "If any clause is ambiguous or risks meaning loss during summarisation, quote the clause verbatim and flag it rather than paraphrasing. Refuse to summarise if the input is empty or malformed."
