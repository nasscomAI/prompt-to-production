skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections, preserving section numbers and original wording.
    input: A file path string pointing to a .txt policy document.
    output: A structured dict where each key is a section number (e.g. "2.6") and each value is the full text of that section exactly as written in the source file.
    error_handling: If the file is not found, stop and return a clear error message with the file path. If a section number cannot be parsed, include the text under an 'unparsed' key and continue.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant plain-text summary with every clause present, all conditions intact, and section references included.
    input: A structured dict of policy sections as returned by retrieve_policy.
    output: A plain-text summary where each clause is listed with its section number, original binding language preserved, and all conditions stated explicitly.
    error_handling: If a section's meaning cannot be preserved in summary form without loss, quote it verbatim and append the tag [verbatim — meaning loss risk]. Never skip a section silently.