# skills.md

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path to the policy document (.txt format)
    output: Structured numbered sections extracted from the policy
    error_handling: Return an error indicating failure to read the file or parse sections if the file is missing or improperly formatted.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections produced by `retrieve_policy`
    output: A compliant text summary containing clause references
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.
