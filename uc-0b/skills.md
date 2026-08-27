skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents, returning them as structured numbered sections.
    input: File path to the raw `.txt` policy document (e.g., `policy_hr_leave.txt`).
    output: A structured dictionary mapping numbered sections/clauses directly to their raw text representation.
    error_handling: Return a clear error if the file format is invalid, missing, or lacks any clear numbered structure.

  - name: summarize_policy
    description: Consumes structured sections, adhering to agents.md enforcement to produce a complaint summary with explicit clause references.
    input: The outputted structured numbered sections from retrieve_policy over formatted text.
    output: A continuous string representing the finalized summary explicitly attributing policies to their clauses.
    error_handling: Must quote the clause verbatim and affix an embedded FLAG if summarization threatens to alter the fundamental meaning or obligations.
