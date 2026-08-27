# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Reads the raw text file and extracts the numbered clauses precisely without altering text.
    input: "Path to a text file containing the policy document."
    output: "A dictionary with exact clause numbers as keys and verbatim clause text as values."
    error_handling: "If the file is unreadable, returns an error message."

  - name: summarize_policy
    description: Filters and outputs only the required 10 critical clauses exactly as written to ensure zero condition drops or obligation softening.
    input: "Dictionary of all numbered clauses extracted by retrieve_policy."
    output: "A fully compliant summary preserving the exact binding language, formatted clearly without adding external scope."
    error_handling: "If any of the 10 target clauses are missing, appends an [OMISSION ERROR] to the summary."
