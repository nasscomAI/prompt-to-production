# skills.md — UC-0B HR Leave Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and parses it into structured numbered sections (title + clause number + full clause text).
    input: input_path (str) — path to the policy .txt
    output: dict — {document, meta, sections: [{title, clauses: [{number, text}]}]}
    error_handling: Missing or unreadable file exits with an error message; a file with no numbered clauses is rejected instead of being summarised.

  - name: summarize_policy
    description: Produces a clause-complete summary from structured sections, quoting each clause verbatim in compressed form and flagging multi-condition obligations.
    input: parsed (dict) — output of retrieve_policy
    output: str — full summary text including a completeness check for the 10 critical clauses
    error_handling: Clauses that cannot be summarised without meaning loss are retained verbatim and flagged; the completeness check reports any critical clause that is missing.