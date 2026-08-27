skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from a given path and returns its content
      as structured numbered sections (e.g. sections 1–8 with subsections).
    input: >
      A file path (string) pointing to a plain-text policy document.
    output: >
      A list of objects, each with `section` (str, the heading),
      `clauses` (list of dicts with `number` and `text` fields).
    error_handling: >
      If the file is missing, unreadable, or empty, raise FileNotFoundError
      with a descriptive message. Do not attempt to parse the policy of a
      different format.

  - name: summarize_policy
    description: >
      Takes the structured sections from retrieve_policy and produces a
      compliant plain-text summary with numbered clause references.
    input: >
      List of structured sections as produced by retrieve_policy.
    output: >
      A plain-text string containing the summary, where every numbered
      clause is preserved with its full obligation and all conditions.
    error_handling: >
      If any of the 10 critical clauses (2.3–2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
      is missing from the input, raise a ValueError listing the missing
      clauses. Never insert fabricated content to fill gaps.
