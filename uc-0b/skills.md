skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns its content as structured numbered sections.
    input: File path (string) to a .txt policy file, e.g. ../data/policy-documents/policy_hr_leave.txt
    output: A list of structured clause objects, each with clause_number, raw_text, and binding_verb fields
    error_handling: If the file cannot be found or contains no numbered clauses, raise a clear error rather than returning an empty or partial result silently

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary that preserves every clause and condition.
    input: A list of structured clause objects returned by retrieve_policy
    output: Plain text summary written to summary_hr_leave.txt, with every clause number referenced
    error_handling: If a clause cannot be summarized without meaning loss, it must be quoted verbatim in the output and flagged with a note rather than silently paraphrased or dropped