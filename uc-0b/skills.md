# skills.md — UC-0B Policy Summary Agent

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections, preserving clause numbering, hierarchy, and original wording verbatim.
    input: File path to a plain-text policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: Ordered list of sections, each containing the clause number (e.g., 2.3, 5.2), the section heading, and the full clause text exactly as written in the source.
    error_handling: If the file path is invalid or the file is empty, return an error with the message "Policy file not found or empty" and halt — do not proceed with a partial or assumed document.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary that preserves every numbered clause, all multi-condition obligations, and the exact binding language from the source.
    input: Ordered list of structured sections as returned by retrieve_policy, each containing clause number, heading, and full clause text.
    output: A plain-text summary (written to summary_hr_leave.txt) where every clause is represented with its clause reference, core obligation, and original binding verb intact. Multi-condition clauses (e.g., 5.2 requiring both Department Head AND HR Director) retain all conditions. Clauses that cannot be condensed without meaning loss are quoted verbatim and flagged as '[VERBATIM — cannot summarize without meaning loss]'.
    error_handling: If a clause contains multi-condition obligations that risk condition-drop during summarization, the skill must preserve all conditions explicitly rather than simplifying. If input sections are malformed or missing clause numbers, flag the affected sections as '[PARSE ERROR — original text preserved]' and include the raw text to prevent silent omission.
