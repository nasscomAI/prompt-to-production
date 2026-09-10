# skills.md

skills:
  - name: retrieve_policy
    description: Load HR-POL-001 .txt policy file and return content as structured numbered sections.
    input: "input_path (string path to policy_hr_leave.txt, UTF-8 plain text). Example: '../data/policy-documents/policy_hr_leave.txt'."
    output: "Dict of section number -> {clause number -> clause text verbatim}, e.g. {'2': {'2.3': 'Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.', ...}}. Preserves original wording, numbers, and binding verbs with no paraphrase."
    error_handling: If file is missing, unreadable, or empty, raise FileNotFoundError/ValueError with the path — never return invented clauses, never fall back to external HR knowledge.

  - name: summarize_policy
    description: Take structured policy sections and produce compliant summary with clause references per agents.md enforcement.
    input: "Dict from retrieve_policy (structured numbered sections). Only the 10 target clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are summarised, one tagged section each."
    output: "Plain-text summary at output_path with one '[X.Y]' tagged line/block per clause, preserving all numeric conditions and binding verbs, with no added sentences. Example: '[5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.'"
    error_handling: If a clause text is missing from input, emit its tag with source quote unavailable and flag [VERBATIM — summarisation would lose meaning] rather than inventing wording. If a clause cannot be compressed without dropping a condition, quote it verbatim with the [VERBATIM] flag. Never omit a clause, never add untraceable sentences.
