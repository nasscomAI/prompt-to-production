# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured
      numbered sections.
    input: >
      Path to a .txt policy file as a string.
    output: >
      A list of section objects, each with keys: section_number (string),
      heading (string), content (string).
    error_handling: >
      If file does not exist or is not a .txt file, raise a clear error.
      If file has no numbered sections, return the full text as a single
      section with section_number "0".

  - name: summarize_policy
    description: >
      Takes structured policy sections and produces a compliant summary
      that preserves every clause, every condition, and every binding verb.
    input: >
      A list of section objects from retrieve_policy.
    output: >
      A string summary with each clause referenced by its section number,
      preserving all conditions and binding verbs verbatim where needed.
    error_handling: >
      If a section contains language that cannot be paraphrased without
      meaning loss, quote it verbatim and append [FLAG] to that entry.
      If input is empty, return an empty string.
