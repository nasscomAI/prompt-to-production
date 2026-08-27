# skills.md

skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections.
    input: String representing the file path to the .txt policy document.
    output: Structured text containing numbered sections of the policy document.
    error_handling: Log an error and return formatting failure if the file is missing, not a .txt file, or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references.
    input: Structured text containing numbered sections of the policy document.
    output: A summary string where every numbered clause is present, multi-condition obligations preserve all conditions, and no external information is added.
    error_handling: Raise a validation error if any mandatory numeric clause is missing, or if multiple conditions are not preserved accurately in the output summary.
