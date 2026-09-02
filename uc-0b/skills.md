# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its content as structured numbered sections (clause number → verbatim clause text), preserving section titles.
    input: filesystem path to a UTF-8 .txt policy file with numbered clauses of the form "N.N text" under "N. TITLE" headings.
    output: list of section dicts, each with keys section_no (int), title (str), clauses (list of dicts with number and text); clause text is verbatim, whitespace-normalised.
    error_handling: a missing or unreadable file exits with a clear error message; lines that look like clause numbers but have no text are kept with an empty-text marker so the summary still accounts for them; a clause number that fails to parse is logged to stderr, never silently dropped.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant clause-referenced summary where every clause appears exactly once with its binding verb and all conditions preserved.
    input: the structured section list from retrieve_policy plus an output filesystem path.
    output: summary_hr_leave.txt containing a header naming the source document, one line per clause in the form "N.N — <clause text>", and a trailing verification block stating clauses summarised vs clauses found in source.
    error_handling: if any clause text is empty the line is emitted as "N.N — [NO TEXT IN SOURCE — flagged for review]"; if the clause count in the summary does not equal the clause count parsed from the source, the script exits non-zero after writing the file so the mismatch is visible.
