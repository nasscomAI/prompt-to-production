# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a plaintext (.txt) policy document and parses its content into structured, validated numbered sections and sub-clauses with metadata.
    input: `file_path` (str, path to the input policy .txt file).
    output: dict containing `doc_title` (str), `doc_ref` (str), `version` (str), `effective_date` (str), and `sections` (list of dicts, each with `section_number` (int), `section_title` (str), and `clauses` (list of dicts containing `clause_id` (str), `text` (str), and `binding_verbs` (list of str))).
    error_handling: Raises `FileNotFoundError` if the file does not exist; raises `ValueError` if the file is empty, unreadable, or missing required numbered section headers.

  - name: summarize_policy
    description: Takes structured policy sections and generates a comprehensive, lossless summary adhering strictly to all clause preservation, multi-condition fidelity, and binding verb rules.
    input: `structured_sections` (dict or list of structured sections containing parsed clauses from `retrieve_policy`) and optional `strict_mode` (bool, default True).
    output: str (or summary file content) containing structured text organized by section and clause identifiers, preserving all multi-condition approvals, exact deadlines, forfeiture conditions, and strict prohibitions without scope bleed or obligation softening.
    error_handling: If any clause is missing from the output, if a multi-condition obligation drops a condition/approver, or if binding modal verbs are softened, the skill rejects the summary draft and quotes the exact source clause verbatim flagged with `[VERBATIM QUOTE]`.
