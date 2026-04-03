skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: String representing the absolute or relative file path to the policy text document.
    output: A structured object containing extracted numbered sections and their corresponding verbatim text.
    error_handling: If the file is missing, unreadable, or missing clear structures, return an error indicating failure to parse.

  - name: summarize_policy
    description: Takes structured sections of a policy and produces a compliant summary with clause references.
    input: Structured policy sections with explicit clause numbering.
    output: A detailed text summary incorporating all clauses, mapping back to their original references without condition drops.
    error_handling: If a clause is ambiguous or cannot be summarized without altering its meaning, return a verbatim quote of the clause marked with a flag.
