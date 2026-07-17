# skills.md — UC-0B

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: str — file path to the policy .txt file
    output: dict — keys are section numbers (e.g. "2.3"), values are the full text of each section
    error_handling: If file is not found or empty, returns an empty dict and prints an error message

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, preserving all conditions and obligations.
    input: dict — structured sections from retrieve_policy
    output: str — formatted summary text with numbered clause references
    error_handling: If a section is missing or empty, flags it as "[SECTION MISSING]" in the output
