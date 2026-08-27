* name: "retrieve_policy"
  description: "Loads the HR leave policy text file and structures it into numbered clauses for downstream processing."
  input:
  type: "string"
  format: "file path to .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)"
  output:
  type: "object"
  format: "structured representation of policy with numbered sections and clauses (e.g., { '2.3': '...', '2.4': '...', ... })"
  error_handling:

  * "If file path is invalid or file cannot be read, return an explicit error indicating file access failure"
  * "If content is empty or not a valid policy document, return an error indicating invalid input content"
  * "If clauses cannot be reliably identified or structured, return an error indicating ambiguous or unstructured document"
  * "Do not infer or fabricate missing clauses; return only what is explicitly present in the source"

* name: "summarize_policy"
  description: "Generates a clause-complete, meaning-preserving summary of the policy using structured sections with explicit clause references."
  input:
  type: "object"
  format: "structured numbered clauses (e.g., { '2.3': '...', '2.4': '...', ..., '7.2': '...' })"
  output:
  type: "string"
  format: "text summary including all clauses (2.3–7.2) with preserved obligations, conditions, and references"
  error_handling:

  * "If any of the 10 required clauses are missing, return an error indicating clause omission"
  * "If a clause contains multi-condition obligations and any condition cannot be preserved, return an error indicating condition loss risk"
  * "If summarization introduces external assumptions or scope bleed phrases, reject output and return an error indicating scope violation"
  * "If a clause cannot be summarized without meaning loss, include it verbatim and flag it explicitly"
  * "If input format is invalid or incomplete, return an error indicating invalid structured input"
