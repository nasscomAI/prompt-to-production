# skills.md — UC-0B Policy Summary

skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path string to a .txt policy document.
    output: Dictionary mapping section numbers to section text content.
    error_handling: Returns empty dict and logs error if file not found or unreadable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Dictionary of section_number → section_text from retrieve_policy.
    output: String summary with every clause preserved, conditions intact, and clause numbers cited.
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it.
