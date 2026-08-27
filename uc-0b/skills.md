skills:

name: retrieve_policy
description: Load a policy text file and extract numbered clauses as structured sections.
input: Path to a .txt policy document (string file path).
output: List of numbered policy clauses as structured text sections.
error_handling: If the file cannot be read or contains no numbered clauses, return an error message and halt processing rather than guessing missing policy content.

name: summarize_policy
description: Generate a clause-preserving summary from structured policy sections.
input: List of numbered policy clauses extracted from the source document.
output: Text summary where every clause number and obligation from the source document is preserved.
error_handling: If a clause cannot be summarized without changing meaning, include the clause verbatim and flag it for review rather than modifying or omitting it.

