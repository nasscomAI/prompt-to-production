* name: retrieve_policy
  description: Loads a policy text file and extracts its content into structured numbered clauses.
  input:
  type: file
  format: "Plain text file (.txt) containing policy document with numbered clauses (e.g., 2.3, 2.4, etc.)."
  output:
  type: object
  format: "Structured representation of clauses as a list or dictionary keyed by clause numbers with corresponding text content."
  error_handling:

  * "If the file is missing, unreadable, or path is invalid, abort and return an explicit error message."
  * "If the file content is empty, return an error indicating no policy content available."
  * "If numbered clauses cannot be reliably extracted, return a failure indicating malformed structure."
  * "Ensure all expected clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present; if any are missing, flag an error."
  * "Do not infer or fabricate missing clauses; only extract what exists in the source document."

* name: summarize_policy
  description: Generates a compliant summary of the policy using structured clauses while preserving all obligations and conditions.
  input:
  type: object
  format: "Structured clauses as extracted by retrieve_policy, keyed by clause numbers with full text."
  output:
  type: file
  format: "Plain text file containing a summary where each clause is represented with its number and accurately preserved meaning."
  error_handling:

  * "If any required clause is missing from input, abort and return an error indicating incomplete clause set."
  * "If a clause contains multiple conditions, ensure all are preserved; if not possible, quote the clause verbatim and flag it."
  * "If summarization risks dropping conditions (e.g., Clause 5.2 missing one approver), regenerate to include all conditions explicitly."
  * "If output introduces information not present in the source, remove it and regenerate to strictly match source content."
  * "If binding verbs (must, will, requires, not permitted) are weakened or altered, correct them to match original strength."
  * "If scope bleed is detected (e.g., 'typically', 'generally expected'), remove such language and regenerate."
  * "Ensure every clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is included in the output; if not, regenerate."
  * "If ambiguity prevents accurate summarization, quote the clause verbatim and clearly flag it."
