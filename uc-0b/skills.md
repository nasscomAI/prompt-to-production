skills:
  - name: retrieve_policy
    description: Load a .txt policy file from disk and return its content as structured numbered sections.
    input: A file path string pointing to a .txt policy document.
    output: A list of structured sections, each containing the clause number and its full text, preserving the original document order.
    error_handling: If the file is not found or cannot be read, raise a descriptive FileNotFoundError. If the document has no numbered sections, return the raw text and flag it for manual review.

  - name: summarize_policy
    description: Take the structured numbered sections from retrieve_policy and produce a clause-by-clause compliant summary with clause references, preserving all binding obligations and multi-condition rules.
    input: A list of structured policy sections (each with a clause number and clause text) as returned by retrieve_policy.
    output: A plain-text summary file (summary_hr_leave.txt) where every numbered clause is cited, all multi-condition obligations are intact, and no external information is added.
    error_handling: If a clause cannot be summarised without loss of meaning, quote it verbatim and prefix it with "VERBATIM QUOTE" in the output. If any numbered clause is missing from the input sections, log a warning and flag the output as INCOMPLETE.
