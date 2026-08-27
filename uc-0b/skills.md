skills:

* name: retrieve_policy
  description: Loads a .txt policy file and returns its contents as structured numbered sections.
  input:
  type: string
  format: file path to a .txt document (e.g., ../data/policy-documents/policy_hr_leave.txt)
  output:
  type: object
  format: structured representation of the policy with numbered clauses and their full text
  error_handling:

  * If the file path is invalid or file cannot be read, return an explicit file access error
  * If the file content is empty or unstructured, return an error indicating invalid policy format
  * If numbered clauses cannot be reliably identified, return an ambiguity error and halt processing
* name: summarize_policy
  description: Generates a clause-preserving summary from structured policy sections with explicit clause references.
  input:
  type: object
  format: structured numbered sections of the policy document
  output:
  type: string
  format: text summary including all required clause references with preserved obligations and conditions
  error_handling:

  * If any of the required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing, return a clause omission error
  * If a clause contains multi-condition obligations and any condition cannot be preserved, return a condition loss error and quote the clause verbatim
  * If the summary introduces information not present in the source, return a scope bleed error
  * If summarization risks altering the original meaning or softening binding obligations, return an obligation integrity error and require verbatim inclusion
