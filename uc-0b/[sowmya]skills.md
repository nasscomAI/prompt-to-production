skills:
  - name: retrieve_policy
    description: Loads an input text policy file and returns its content as structurally parsed numbered sections.
    input: string (file path to the .txt policy document)
    output: list of dictionaries (structured sequence of numbered sections)
    error_handling: Trigger a failure if the file is missing or unreadable, and emit an explicit warning to prevent clause omission if structural elements are malformed.
  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that preserves all conditions and explicitly references source clauses.
    input: list of dictionaries (the structured sections extracted from the policy)
    output: string (compliant summary text)
    error_handling: Quote verbatim and flag any clause that risks meaning loss or obligation softening, and strictly block any scope bleed insertions not present in the source text.
