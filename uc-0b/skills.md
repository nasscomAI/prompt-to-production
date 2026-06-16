# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of numbered sections, each with a section heading and clause lines.
    input: File path string pointing to a UTF-8 encoded .txt policy document.
    output: List of dicts, each with keys section_number, section_heading, and clauses (list of strings).
    error_handling: If the file is missing or unreadable, raise a clear FileNotFoundError with the path. If a section has no detectable heading, label it UNLABELLED_SECTION and continue.

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-by-clause compliant summary with clause references and EXACT_QUOTE flags where needed.
    input: List of section dicts produced by retrieve_policy, plus the list of key clause IDs that must be verified present.
    output: Plain-text summary string where each clause is referenced by number, binding verbs are preserved, and any verbatim-required clause is marked EXACT_QUOTE.
    error_handling: If a required key clause is not found in the structured sections, append a MISSING_CLAUSE warning for that clause ID rather than silently omitting it.
