# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      input_path (str): path to the policy .txt file.
    output: >
      A list of section dictionaries, each with keys:
      section_number (str), section_title (str), clauses (list of dicts with clause_number and text).
    error_handling: >
      If the file cannot be read, raise an error with the file path.
      If the file has no recognizable numbered sections, return the raw text with a warning.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary with clause references.
    input: >
      sections (list): structured sections from retrieve_policy.
    output: >
      A plain text summary where each line starts with the clause number,
      followed by a faithful summary preserving all conditions, binding verbs,
      and specific numbers. Clauses that cannot be shortened without meaning loss
      are quoted verbatim with a [VERBATIM] flag.
    error_handling: >
      If a clause is empty or malformed, include it with a [REVIEW NEEDED] flag.
      Never silently skip a clause.
