# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a .txt policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: Dictionary with "metadata" (header lines, document reference, version, effective date) and "sections" (list of sections, each with number, title, and list of clauses keyed by number and text).
    error_handling: Raises a clear error when the file cannot be read or contains no numbered sections; non-section lines are treated as metadata, never silently dropped.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured sections as returned by retrieve_policy.
    output: A clause-preserving summary string where every numbered clause is reproduced verbatim with all conditions intact, followed by a verification block (clause count, inventory check, flags).
    error_handling: Raises ValueError if any clause from the README inventory is missing from the summary; any clause that cannot be reproduced without meaning loss is flagged rather than guessed.

  - name: retrieve_complaints
    description: Loads a city complaint .csv and returns its rows with the original column order.
    input: Path to a .csv complaint file (e.g. ../data/city-test-files/test_ahmedabad.csv).
    output: Dictionary with "fieldnames" (original column order) and "rows" (list of row dicts).
    error_handling: Raises a clear error when the file cannot be read; rows are returned as-is, never dropped or reordered.

  - name: summarize_complaints
    description: Takes structured CSV rows and produces a row-preserving result with a summary column for every row.
    input: Structured rows as returned by retrieve_complaints.
    output: Dictionary with "fieldnames" (original columns plus "summary" and "flag") and "rows", where every source row is preserved and each row's summary is built solely from its own field values.
    error_handling: Raises ValueError if the output row count differs from the input; rows with missing fields are flagged NEEDS_REVIEW rather than guessed.
