# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections keyed by clause number.
    input: Path to a UTF-8 .txt policy document whose clauses are numbered N.N at line starts, with wrapped continuation lines beneath.
    output: Ordered dict mapping clause number strings ("2.3") to full clause text (wrapped lines joined); section headers excluded.
    error_handling: Missing or unreadable file raises OSError to the caller; an empty or header-only file yields an empty dict rather than crashing.

  - name: summarize_policy
    description: Produces a compliant summary in which every clause number from the input appears, with obligation and condition sentences preserved verbatim.
    input: Dict mapping clause numbers to clause text, as returned by retrieve_policy (may also be built by any equivalent parser).
    output: UTF-8 summary string with one "N.N ..." line per clause; clauses whose sentences could not be safely filtered carry a [QUOTED VERBATIM] flag on the following line; empty input yields the exact refusal line "No numbered clauses found in source document."
    error_handling: Never raises for dict input; missing keys, None values, or non-string clause text are treated as empty and fall through to the verbatim/refusal path.
