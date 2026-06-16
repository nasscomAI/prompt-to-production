# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections, ready for summarisation.
    input: >
      A single file path (string) to a .txt policy document.
      Example: file_path="../data/policy-documents/policy_hr_leave.txt"
    output: >
      A list of section dicts, each with:
        clause_id   — the clause number as a string (e.g. "2.3", "5.2")
        heading     — clause heading text if present, else empty string
        body        — full verbatim clause text as a string
      Example: [{"clause_id": "2.3", "heading": "Advance Notice", "body": "Employees must submit..."}]
    error_handling: >
      If file_path does not exist or cannot be read, raise FileNotFoundError with a clear message.
      If the file is empty or contains no recognisable numbered clauses, raise ValueError
      describing what was found. Never return a partial or empty section list silently.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant clause-by-clause summary that preserves all obligations, binding verbs, and multi-condition requirements exactly as in the source.
    input: >
      A list of section dicts as returned by retrieve_policy (clause_id, heading, body),
      plus an output file path (string) where the summary will be written.
      Example: sections=[...], output_path="uc-0b/summary_hr_leave.txt"
    output: >
      A .txt file at output_path where each line follows the format:
        [clause_id] <summary sentence using source binding verb>
        flag: VERBATIM_REQUIRED  ← appended on the same clause line if meaning loss risk detected
      All 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must appear.
      Also prints to stdout: total clauses summarised, count of VERBATIM_REQUIRED flags.
    error_handling: >
      If any required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is absent
      from the input sections, raise ValueError listing the missing clause IDs — never silently
      skip a clause or produce a summary with gaps.
      If a clause body contains multiple conditions joined by AND/and, preserve all of them;
      flag the clause as VERBATIM_REQUIRED rather than risk dropping a condition.
