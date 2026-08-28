

skills:
  - name: retrieve_policy
    description: Load the supplied HR leave policy text and return its content as structured numbered clauses without altering the source wording.
    input: A UTF-8 .txt policy-file path, such as ../data/policy-documents/policy_hr_leave.txt.
    output: An ordered list or mapping of clause references to their verbatim policy text, preserving clause numbers, conditions, deadlines, approvals, thresholds, and consequences.
    error_handling: Report a clear error when the file is missing, unreadable, empty, or not a text file, and never substitute external policy content.

  - name: summarize_policy
    description: Produce a complete clause-referenced HR leave policy summary that preserves the meaning and force of every required obligation.
    input: Structured numbered policy clauses returned by retrieve_policy.
    output: A formal summary containing clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2, with all conditions and consequences preserved and any meaning-sensitive clause quoted and flagged.
    error_handling: Identify missing or ambiguous clauses, do not guess or fill gaps with external knowledge, and quote and flag any clause that cannot be summarized without loss of meaning.
