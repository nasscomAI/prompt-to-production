# skills.md

skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts its structured numbered sections.
    input: Path to policy text file.
    output: Data structure containing mapped clause numbers and their raw text content.
    error_handling: Raise file not found or formatting errors if sections cannot be parsed.

  - name: summarize_policy
    description: Takes the structured policy text and summarizes each key clause while preserving all conditions.
    input: Structured clause mapping from retrieve_policy.
    output: Text summary of the critical clauses with section citations, containing zero scope bleed.
    error_handling: Verbatim fallback when clause details are highly specific and cannot be condensed without meaning loss.
