# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: File path to the policy .txt file.
    output: A dictionary or object containing structured numbered sections (e.g., "2.3": "text").
    error_handling: Return an error if the file cannot be found or is not readable.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that satisfies all enforcement rules in agents.md.
    input: Structured sections from retrieve_policy.
    output: A formatted summary text file content with mandatory clause references.
    error_handling: If a section is missing or unparseable, skip it and add a [MISSING] flag to the final report.
