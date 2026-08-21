# skills.md — UC-0B HR Leave Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: path to a UTF-8 policy .txt file with `N.N` numbered clauses under `N. TITLE` section headers.
    output: ordered list of clauses {id, section_no, section_title, body} with wrapped lines joined and whitespace collapsed.
    error_handling: unreadable file → ERROR line + exit code 1; zero clauses parsed → ERROR line + exit code 1 (wrong input file), never an empty summary.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, quoting obligation sentences verbatim.
    input: ordered clause list from retrieve_policy plus the source path for header metadata.
    output: summary text where every clause id appears, normative sentences are verbatim quotes, lossy clauses carry a QUOTED_VERBATIM flag, and a FLAGS section lists them.
    error_handling: pre-write verification gate re-checks the 10 ground-truth clauses and the dual approvers of 5.2 inside the generated text; on any failure prints VERIFICATION FAILED with reasons and exits 1 WITHOUT writing the output file.
