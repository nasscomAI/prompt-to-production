skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and extracts its content as structured, numbered sections.
    input: >
      A string representing the path to the policy .txt file.
      Format: absolute or relative file path (e.g., '../data/policy-documents/policy_hr_leave.txt').
    output: >
      A dictionary mapping clause IDs (str) to the exact text of each clause (str).
    error_handling: >
      If the file is missing or unreadable, return a descriptive error dictionary or string (e.g., {"error": "File not found"}).
      If the format is invalid or clauses are missing, do not crash but return the structured sections successfully parsed so far.

  - name: summarize_policy
    description: >
      Takes structured clause sections and produces a compliant summary with correct clause references,
      preserving all conditions, binding obligations, and clauses without dropping details or adding scope bleed.
    input: >
      A dictionary of structured sections mapping clause numbers to text (output of retrieve_policy).
    output: >
      A formatted summary string containing the verbatim or fully preserved representation of all required clauses.
    error_handling: >
      If any mandated clause is completely missing from the input, explicitly flag the omission in the output summary.
      If a clause is structurally complex and cannot be summarised without meaning loss (e.g. multi-condition obligations like 'Department Head AND HR Director'), 
      quote it verbatim and flag it rather than dropping a condition.
      If out-of-scope information is detected (scope bleed), remove it or refuse execution, citing the refusal condition.
