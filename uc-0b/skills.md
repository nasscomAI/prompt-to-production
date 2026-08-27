# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections for clause-by-clause processing.
    input: Path to a .txt policy document (e.g. policy_hr_leave.txt).
    output: A list of dictionaries, each with keys: section_number (e.g. "2.3"), content (the full text of that clause), binding_verb (the key obligation verb extracted from the clause).
    error_handling: If the file does not exist or cannot be read, raises a FileNotFoundError with the file path. If the file has no recognizable numbered sections, returns the full content as a single section with section_number "FULL" and logs a warning that clause-level granularity is not available.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: A list of structured sections from retrieve_policy, each with section_number, content, and binding_verb.
    output: A text summary string where each clause is referenced by number, its obligation is stated with the binding verb preserved, and all conditions are included. Written to the specified output file path.
    error_handling: If any of the 10 critical clauses (2.3–7.2) are missing from the input, the summary includes a [MISSING CLAUSE X.X] placeholder for each absent clause and flags the output with a warning. If a clause's meaning cannot be compressed without loss, it is quoted verbatim with a [VERBATIM] flag.
