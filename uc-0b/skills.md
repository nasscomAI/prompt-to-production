# skills.md — HR Policy Summarizer

skills:
  - name: retrieve_policy
    description: Parses a .txt HR policy and extracts specific numbered clauses into a mapping. It identifies clause headers (e.g., "5.2") and their corresponding obligations.
    input: File path (string) and an optional list of target clause IDs.
    output: A JSON object {clause_id: obligation_text}.
    error_handling: Return "Mapping Error" if required clauses (like 5.2 or 7.2) are missing or if numbering is ambiguous.

  - name: summarize_policy
    description: Generates a summary for each clause while strictly preserving binding verbs ("must", "will") and multi-party approval requirements.
    input: Output from retrieve_policy and the Ground Truth mapping from README.md.
    output: A summary where each line is prefixed by its clause ID. If a clause contains complex multi-conditions (like 5.2's dual approval) that cannot be safely summarized, it maintains the verbatim text and adds a [VERBATIM] flag.
    error_handling: Refuse and return "Condition Drop Error" if the summary loses any condition (e.g., omitting "HR Director") or if binding strength is softened.
