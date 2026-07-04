# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and return its content as structured numbered sections for downstream summarization.
    input: A file path to a .txt policy document.
    output: A structured representation of the document with numbered clauses or sections and their original text.
    error_handling: If the file is missing, unreadable, or does not contain parseable numbered clauses, return a clear error and stop rather than guessing.

  - name: summarize_policy
    description: Convert structured policy sections into a compliant summary that preserves all clauses, conditions, and binding language.
    input: A structured representation of numbered policy sections from retrieve_policy.
    output: A clause-by-clause summary that includes clause references, preserves all required conditions, and uses verbatim quotes when necessary to avoid meaning loss.
    error_handling: If a required clause is missing or a condition is likely to be dropped, preserve the exact source wording for that clause and flag it instead of paraphrasing loosely.
