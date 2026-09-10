# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads an HR policy .txt file and returns its content as structured numbered sections.
    input: File path (string) to a .txt policy document such as policy_hr_leave.txt.
    output: An ordered dict mapping clause numbers (e.g. "2.3") to clause text (string), plus document header metadata.
    error_handling: Raises FileNotFoundError with a clear message if the file is missing. If no numbered clauses are found, raises ValueError instead of returning an empty summary.

  - name: summarize_policy
    description: Turns structured policy sections into a compliant summary with a cited bullet per clause.
    input: Ordered dict of clause number to clause text from retrieve_policy.
    output: A plain-text summary (string) with one cited bullet per numbered clause, preserving all binding verbs, numbers, dates, and approver conditions, with no added information.
    error_handling: If any expected critical clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is absent from the input, the summary states "CLAUSE MISSING IN SOURCE: [X]" for that clause instead of inventing content.
