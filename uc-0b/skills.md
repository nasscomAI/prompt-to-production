skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content organized as structured, numbered sections.
    input: A file path pointing to the policy `.txt` document (`--input`).
    output: A structured string or dictionary containing the extracted clauses, strictly maintaining the original numbering.
    error_handling: If the file cannot be found or read, log an error and exit. If a section is unnumbered, append it to the preceding section rather than inventing a new number.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that explicitly references every clause and preserves all multi-condition obligations.
    input: The structured, numbered sections extracted by retrieve_policy.
    output: A written summary text file (`--output`) where every numbered clause is summarized without any added assumptions or standard practices.
    error_handling: If a clause contains ambiguous or heavily nested legal language that cannot be summarized without losing strict meaning, quote the clause verbatim and flag it in the summary output.
