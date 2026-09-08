skills:
  - name: retrieve_policy
    description: Loads a policy text file, validates its structure, and parses it into numbered sections and individual numbered clauses.
    input: File path to policy document (string, e.g. path to policy_hr_leave.txt).
    output: Structured dictionary containing document metadata (title, reference, version, effective date) and list of sections with individual numbered clauses.
    error_handling: Raises FileNotFoundError if file is missing, or ValueError if document does not contain valid numbered sections.

  - name: summarize_policy
    description: Processes structured policy clauses and produces an authoritative summary ensuring complete clause retention, full condition preservation, and zero scope bleed.
    input: Structured policy dictionary from retrieve_policy, output file path.
    output: Writes compliant formatted policy summary text to output file.
    error_handling: Asserts that all mandatory numbered clauses are present in the final output; flags and appends any missing clause verbatim before saving.
