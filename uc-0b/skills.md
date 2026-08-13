# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections, preserving clause numbers, headings, and full text.
    input: A string — file path to a .txt policy document.
    output: A list of dicts, each with keys — section (e.g. "2. ANNUAL LEAVE"), clause_number (e.g. "2.3"), clause_text (full verbatim text of the clause).
    error_handling: If the file is not found or unreadable, prints an error and exits. If a line cannot be parsed into a clause, it is attached to the preceding clause as continuation text.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant clause-by-clause summary that preserves all obligations, conditions, binding verbs, and numeric thresholds.
    input: A list of structured clause dicts from retrieve_policy.
    output: A text string — the summary organized by section heading, with one summary line per clause, preserving clause number references, binding verbs, all conditions, and all numeric values.
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it with "[VERBATIM — meaning loss risk]". Never silently omits a clause.
