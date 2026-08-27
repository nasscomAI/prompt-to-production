# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections, ensuring every numbered clause is captured for downstream processing.
    input: File path to the policy .txt file.
    output: A structured collection (e.g., list of dictionaries) containing the clause number and its raw text.
    error_handling: Return an error if the file cannot be accessed or if the text does not contain identifiable numbered clauses.

  - name: summarize_policy
    description: Transforms structured policy clauses into a concise summary while strictly enforcing that no conditions are dropped or softened.
    input: Structured policy sections (output from retrieve_policy).
    output: A summary string where every point is mapped to its original clause number, preserving all multi-condition obligations.
    error_handling: If a summary results in meaning loss or "obligation softening" (e.g., dropping a required approver), the skill must instead quote the clause verbatim and flag it as 'SUMMARIZATION_FAILURE'.

