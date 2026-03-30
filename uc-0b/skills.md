skills:
  - name: retrieve_policy
    description: Loads a plaintext policy document and extracts its contents into discrete, structured numbered sections.
    input:
      type: file_path
      format: Path to the .txt policy file (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output:
      type: array
      format: A list of structured objects containing the numbered clause identifier and its corresponding verbatim text payload.
    error_handling: Halts execution if the file is missing or unreadable; if the source text lacks clear structural numbering, it captures the raw text without making assumptions or hallucinating section numbers.
  - name: summarize_policy
    description: Generates a compliant summary from structured sections while preserving all core obligations, multi-conditions, and explicit clause references.
    input:
      type: array
      format: Structured numbered sections provided by the retrieve_policy skill.
    output:
      type: string
      format: A final text summary containing explicit clause references and retaining original binding verbs.
    error_handling: Explicitly counteracts clause omission by halting if any input clause is missing from the output; prevents scope bleed by strictly rejecting generalizations or assumed standard practices not found in the source; prevents condition drops and obligation softening by quoting clauses verbatim and appending a flag when they cannot be summarized without losing original meaning.
