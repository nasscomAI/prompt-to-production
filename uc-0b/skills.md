# skills.md

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: file_path (string)
    output: sectioned_text (dict with clause numbers as keys)
    error_handling: System should refuse if the file does not exist or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: sectioned_text (dict)
    output: serialized_summary (string)
    error_handling: System should flag any clause that cannot be summarized without losing multi-condition obligations.
