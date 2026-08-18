# skills.md

skills:
  - name: retrieve_policy
    description: Loads a text-based policy file and parses it into structured sections based on numbering.
    input: String path to the `.txt` policy file.
    output: List of dictionaries, each containing 'clause_id' and 'text'.
    error_handling: Refuses to process if file format is not .txt or if numbering is completely absent.

  - name: summarize_policy
    description: Iterates through policy sections to produce a condensed version that preserves all binding conditions.
    input: List of structured policy sections.
    output: A string containing the summarized policy with mandatory clause references.
    error_handling: If a section contains complex nested conditions, it defaults to verbatim extraction with a [VERBATIM] flag.
