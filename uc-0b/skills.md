skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: file path (string)
    output: dictionary mapping section names to text blocks or structured numbered sections (dict)
    error_handling: Raises FileNotFoundError if missing. Returns empty dict if no structured sections found.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references preserving all conditions
    input: structured numbered sections (dict)
    output: summary text (string)
    error_handling: Quotes clause verbatim if meaning loss is detected during summarization.
