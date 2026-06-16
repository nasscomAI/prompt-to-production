# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections, preserving clause numbers and binding verbs exactly as written.
    input: >
      A single file path (string) pointing to a plain-text policy document.
      Example: input_path="../data/policy-documents/policy_hr_leave.txt"
    output: >
      A dict mapping clause numbers to their full text, preserving the original
      wording verbatim. Structure:
        {
          "2.3": "Employees must submit leave requests 14 days in advance...",
          "2.4": "Written approval is required before leave commences...",
          ...
        }
      Also returns metadata: {"file": filename, "clause_count": N, "clauses_found": [...]}
    error_handling: >
      If the file does not exist, raise FileNotFoundError with a clear message —
      do not proceed to summarisation.
      If fewer than the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4,
      5.2, 5.3, 7.2) are detected, return the parsed result AND a warning listing
      which required clauses were not found — never silently continue with an
      incomplete clause set.

  - name: summarize_policy
    description: Takes the structured clause dict from retrieve_policy and produces a clause-complete summary where every numbered clause is present, all conditions are preserved, and no external content is added.
    input: >
      A dict of clause_number → clause_text as returned by retrieve_policy.
      Example: {"2.3": "Employees must submit...", "5.2": "LWP requires Department Head AND HR Director approval..."}
    output: >
      A plain-text summary string where:
        - Every clause appears as a numbered entry (e.g. "2.3 — ...")
        - Binding verbs (must, will, requires, not permitted) are preserved unchanged
        - Multi-condition obligations list ALL conditions explicitly
        - Any clause that cannot be paraphrased without meaning loss is quoted
          verbatim and tagged [VERBATIM_REQUIRED]
        - No sentence appears that is not traceable to a clause in the input dict
    error_handling: >
      If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4,
      5.2, 5.3, 7.2) is missing from the input dict, abort and raise ValueError
      listing the missing clause numbers — never produce a summary with a known
      omission.
      If a clause contains multiple conditions (e.g. clause 5.2 names two approvers),
      flag it explicitly as MULTI_CONDITION and list each condition on a separate line
      rather than merging them into one sentence.
