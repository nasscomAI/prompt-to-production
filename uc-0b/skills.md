skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file from disk and returns its content parsed into
      a structured dict of numbered sections and clauses, preserving all original
      wording verbatim.
    input: >
      - file_path: string — absolute or relative path to a .txt policy document.
    output: >
      A dict with structure:
        {
          "raw_text": str,                  # full file content
          "sections": {
            "2": {
              "title": "ANNUAL LEAVE",
              "clauses": {
                "2.1": "Each permanent employee is entitled to ...",
                "2.3": "Employees must submit ..."
              }
            },
            ...
          }
        }
      Section numbers are string keys ("2" through "8").
      Clause numbers are dot-notation string keys ("2.1", "5.2", etc.).
    error_handling: >
      If the file does not exist, raise FileNotFoundError with a clear message —
      do not silently return empty content.
      If the file cannot be parsed into sections (e.g. no numbered headings found),
      return {"raw_text": <full content>, "sections": {}} and print a warning.

  - name: summarize_policy
    description: >
      Takes the structured sections dict from retrieve_policy and produces a
      clause-complete, meaning-preserving summary that satisfies all RICE enforcement
      rules from agents.md. Every clause 2.x through 8.x is referenced by number.
      Binding verbs and numerical values are reproduced exactly.
    input: >
      - policy_data: dict — the output of retrieve_policy (must have "sections" key).
      - output_path: string — file path where the summary .txt will be written.
    output: >
      A .txt file written to output_path containing:
      - A header with document reference, version, and date
      - One section per policy section (2 through 8), preserving section titles
      - Each clause cited by number (e.g. "[2.3]") followed by a faithful summary
        sentence that preserves binding verbs and numerical values exactly
      - Any clause flagged [VERBATIM — condition drop risk] or [VERBATIM — meaning
        loss risk] if the clause cannot be safely paraphrased
      Also prints clause coverage count to stdout: "X of Y clauses summarised."
    error_handling: >
      If a clause produces an output that softens a binding verb or drops a condition,
      fall back to quoting that clause verbatim and appending the appropriate flag.
      If output_path cannot be written, raise a clear IOError — do not silently fail.
      Never skip a clause — if a clause cannot be processed, write its raw text with
      a [PROCESSING ERROR] flag rather than omitting it.
