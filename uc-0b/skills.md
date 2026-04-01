# skills.md
skills:
  - name: retrieve_policy
  description: "Load a .txt policy file and return its clauses as structured numbered sections."
  input:
    type: string
    format: "filesystem path to policy .txt (e.g. ../data/policy-documents/policy_hr_leave.txt)"
  output:
    type: object
    format: "dictionary mapping clause numbers (e.g. '2.3') to clause text and metadata"
  error_handling: "If file not found or unreadable, return an error object or raise FileNotFoundError; if parsing fails, return a parse error with invalid lines."

- name: summarize_policy
  description: "Take structured policy sections and produce a compliant summary with clause references."
  input:
    type: object
    format: "structured clause dictionary from retrieve_policy"
  output:
    type: string
    format: "plain text summary listing each clause and obligations, with verbatim flags where needed"
  error_handling: "If input is missing clauses or malformed, raise ValueError or return an error indicating missing clause numbers; preserve all clauses or verbatim fallback."

