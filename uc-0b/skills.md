# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections.
    input: file_path (str) — absolute or relative path to the policy .txt file.
    output: dict mapping clause numbers (e.g. "2.3", "5.2") to their full text as strings.
    error_handling: If file is not found or unreadable, raise FileNotFoundError with the path. If no numbered clauses are detected, raise ValueError stating the document structure is unrecognised — do not attempt to summarise unstructured text.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary preserving all obligations, conditions, and binding verbs, with clause references throughout.
    input: sections (dict) — output of retrieve_policy; clause number → clause text.
    output: str — formatted summary where every clause is present, referenced by number, with all conditions and binding verbs intact; any meaning-loss clauses are quoted verbatim and tagged VERBATIM_REQUIRED.
    error_handling: If a clause is empty or unparseable, include it in the summary as clause [N]: UNPARSEABLE — flagged for manual review. Never skip a clause silently.
