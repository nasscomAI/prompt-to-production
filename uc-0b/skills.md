skills:

name: retrieve_policy
description: Loads the HR leave policy text file and parses it into structured numbered clauses.
input: "String file path to .txt policy document"
output: "Structured data (list or dictionary) of numbered clauses with clause_id and exact clause text"
error_handling: "If file path is invalid or file cannot be read, return an explicit error and stop; if document is empty, return error; if numbered clauses cannot be reliably identified, return error instead of guessing; do not infer or create missing clauses; ensure all clauses are extracted exactly as written without modification"
name: summarize_policy
description: Generates a clause-preserving summary from structured policy sections with explicit clause references.
input: "Structured clauses (list or dictionary with clause_id and text)"
output: "Text summary where each clause is represented with its clause number and summarized content or verbatim quote if needed"
error_handling: "If any clause is missing from input, return error; if summarization risks dropping conditions or obligations (multi-condition clauses), preserve all conditions or quote verbatim and flag it; if output introduces external assumptions or scope bleed, reject and correct; if meaning cannot be preserved, quote the clause exactly and mark it as verbatim; never omit any clause or soften binding language"
