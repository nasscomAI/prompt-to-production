skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections keyed by clause number.
    input: file_path (str, path to a policy .txt file such as policy_hr_leave.txt).
    output: A list of dicts, each with keys clause_number (str, e.g. "5.2") and text (str, the clause's full text), in document order.
    error_handling: If the file does not exist or cannot be read, raises a clear error naming the missing path rather than returning an empty or partial result silently.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary that references every clause number and preserves all conditions.
    input: A list of clause dicts (clause_number, text) as returned by retrieve_policy.
    output: A string containing one summary line per clause, each prefixed with its clause number, plus [VERBATIM] blocks for any clause quoted in full.
    error_handling: If a clause's obligation cannot be condensed without dropping a condition, that clause is quoted verbatim and marked [VERBATIM] instead of being paraphrased or skipped.
