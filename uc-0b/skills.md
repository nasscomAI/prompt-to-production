# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause IDs.
    input: input_path (str — path to .txt file, expected `policy_hr_leave.txt`; must end with .txt and exist)
    output: dict mapping clause_id (str "X.Y") to clause_text (str — whitespace-collapsed verbatim text without the clause number prefix), plus metadata {source: basename, raw_text: full file content}; example {"2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.", "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."}
    error_handling: If path does not end with .txt, file does not exist, file is empty, or no numbered clauses (regex `\d+\.\d+`) found, return error dict {"error": "invalid input — <reason>"} and caller must refuse to summarize; never hallucinate missing clauses; create no output file on error.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary that preserves every clause number, all binding verbs, and all multi-condition obligations with clause references and no scope bleed.
    input: structured_sections (dict from retrieve_policy — clause_id -> verbatim text); optional source_name (str) for header attribution
    output: str — formatted summary text with header including source attribution and one line per clause prefixed "Clause X.Y:" preserving binding verbs (must/will/may/requires/not permitted/are forfeited) and all conditions; 10 ground-truth clauses are rendered with full condition preservation; file written to output_path
    error_handling: If structured_sections contains error key or is missing any of the 10 ground-truth clauses, emit "[FLAG: quoted verbatim — summarisation would lose condition]" for ambiguous clauses and still include all present clauses; if input dict is empty/error, return "[ERROR: invalid input — cannot summarize]" and do not write hallucinated content; never add external phrases ("as is standard practice", "typically in government organisations", "generally expected") and never soften binding verbs.

