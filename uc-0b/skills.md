# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document from disk and returns its content as structured numbered sections, one entry per top-level section heading.
    input: A string — file_path (absolute or relative path to the .txt policy document, e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: A list of dicts, each with keys — section_number (e.g. "2"), section_title (e.g. "MOBILE PHONE AND INTERNET"), and clauses (a list of dicts with clause_number e.g. "2.3" and clause_text as the full verbatim text of that clause). Returns all sections and all clauses without truncation.
    error_handling: If the file path does not exist or cannot be read, raises a FileNotFoundError with the path included in the message and does not return partial content. If the file is empty, raises a ValueError stating the document is empty. Never silently returns an empty structure.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and produces a compliant summary that preserves all clauses, all binding conditions, and all clause references.
    input: A list of section dicts as returned by retrieve_policy — each with section_number, section_title, and a list of clause dicts (clause_number, clause_text).
    output: A plain-text string containing a summary organised by section. Each clause is represented on its own line, prefixed by its clause number, with all binding conditions preserved verbatim or in a lossless paraphrase. Clauses that cannot be paraphrased without meaning loss are quoted verbatim and prefixed with [VERBATIM - clause X.X].
    error_handling: If the input list is empty or None, raises a ValueError and does not produce partial output. If any individual clause is empty or malformed, outputs [SKIPPED - clause X.X: malformed input] for that clause and continues processing the rest. Never silently drops a clause.