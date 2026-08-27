skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content split into structured numbered sections.
    input: File path to a .txt policy document.
    output: A list of dictionaries, each with keys: section_number (str), heading (str), body (str).
    error_handling: If the file is missing or unreadable, raise a clear error listing the expected path. If the file has no numbered sections, return the full text as a single section with section_number "0".

  - name: summarize_policy
    description: Take structured policy sections and produce a compliant summary with every clause preserved and all conditions intact.
    input: A list of section dictionaries (from retrieve_policy), each with section_number, heading, body.
    output: A string summary with each clause referenced by section number, preserving all conditions and binding verbs.
    error_handling: If any obligation in the input has multiple conditions (e.g. "A AND B"), verify both appear in the output. If they do not, refuse to output and return a list of dropped conditions.
