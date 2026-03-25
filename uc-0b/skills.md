# skills.md — UC-0B Rule-Based Policy Skills

skills:
  - name: retrieve_policy
    description: >
      Loads a plain text policy file and partitions it into numbered sections (e.g., 2.3, 5.2).
    input: File path (string) to a .txt policy document.
    output: A dictionary mapping section numbers (strings) to their corresponding clause text (strings).
    error_handling: >
      If the file is missing or unreadable, the skill raises a FileNotFoundError.

  - name: extract_obligation
    description: >
      Identifies the core obligation sentence for each clause using keyword matching
      (e.g., must, requires, not permitted) and preserves it verbatim to ensure 100% fidelity.
    input: A dictionary of sections and their text.
    output: >
      A formatted summary string with lines of the form "Clause X.Y: [Obligation Sentence]".
    error_handling: >
      If no explicit obligation keyword is found in a section, the first sentence is returned.
      If a clause is complex (contains "and" or multiple conditions), the entire clause is preserved.
