skills:
  - name: retrieve_policy
    description: Loads a raw .txt HR policy file and parses its contents into structured, numbered sections for precise referencing.
    input: A string representing the file path to the source .txt policy document.
    output: A structured object (e.g., dictionary or list) mapping each numbered clause to its exact text.
    error_handling: Raises a FileNotFoundError if the document cannot be read. If the document structure is malformed or lacks clear numbered clauses, it raises a parsing error or returns the raw text under a single default section with a warning.

  - name: summarize_policy
    description: Takes the structured policy sections and produces a compliant summary that strictly preserves all obligations, multiple conditions, and clause references.
    input: A structured object (e.g., dictionary) containing the parsed, numbered policy clauses.
    output: A formatted string containing the final summary, ensuring every original numbered clause is accounted for.
    error_handling: If a clause is deemed impossible to summarize without softening its meaning or losing conditions, it outputs the exact verbatim text of the clause and prepends a "[VERBATIM/FLAGGED]" marker to it.
