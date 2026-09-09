skills:
  - name: retrieve_policy
    description: Loads a plaintext policy file and parses its contents into structured numbered sections and clauses.
    input: File path (str) pointing to a policy text file (e.g. policy_hr_leave.txt).
    output: Structured representation (dict or list) of parsed sections with section headers, clause numbers, and clause texts.
    error_handling: Raises FileNotFoundError with a clear error message if the file is missing; raises ValueError if file contains no numbered clauses.

  - name: summarize_policy
    description: Transforms structured policy clauses into an obligation-preserving summary with clause references, strict verbs, and multi-condition preservation.
    input: Structured sections containing numbered clauses.
    output: Plaintext formatted summary string detailing each clause's exact requirements without omitting conditions or introducing scope bleed.
    error_handling: Emits verbatim clause text with an preservation warning if compression might alter legal meaning.
