# skills.md

skills:

- name: retrieve_policy
  description: Loads a plain text policy file and returns the text content parsed as structured numbered sections.
  input: type: string format: File path to a valid .txt document
  output: type: array format: List of objects, each containing a clause number and its corresponding text content
  error_handling: If the input file is invalid, unreadable, or lacks clear numbered sections, the skill will return an error instead of attempting to guess the text structure.

- name: summarize_policy
  description: Takes structured sections and produces a compliant summary with explicit clause references that strictly adheres to the source text.
  input: type: array format: List of objects, each containing a clause number and its corresponding text content
  output: type: string format: Plain text summary that explicitly maps to every provided source clause without omitting details
  error_handling: If the skill cannot summarize a clause without dropping a multi-condition, softening an obligation, or causing meaning loss, it will quote the clause verbatim and flag it. It will also fail explicitly if generation involves scope bleed or hallucinating standard practices not present in the source.
