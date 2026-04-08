# skills.md

skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections.
    input: A string containing the file path to the .txt policy document.
    output: A list or dictionary containing structured numbered sections from the policy.
    error_handling: If the file is not found or is unreadable, raise an error explaining that the .txt file could not be accessed.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references.
    input: A list of structured numbered sections and their corresponding text.
    output: A string containing a compliant summary of the policy with clause references.
    error_handling: Return an explicit error or fallback to quoting verbatim if the summary process encounters an ambiguous clause that could lead to meaning loss.
