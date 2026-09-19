skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and returns its content as ordered, numbered clauses grouped by section.
    input: File path string to the policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: List of dictionaries with keys clause (e.g. "2.3"), section (e.g. "Annual Leave") and text (full clause text, continuation lines joined).
    error_handling: Raises a clear error if the file cannot be read or contains no numbered clauses; ignores separator lines and blank lines; never invents clauses.

  - name: summarize_policy
    description: Takes the numbered clauses and produces a summary that includes every clause with its clause number, checked against the source.
    input: List of clause dictionaries returned by retrieve_policy.
    output: Summary text with one line per clause, plus a report of clauses verified and clauses flagged.
    error_handling: If a summary line loses a number, a required condition or binding verb, or contains invented wording, or if no summary exists for a clause, the clause is quoted verbatim and marked FLAGGED instead of being paraphrased.