# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and returns its content as structured numbered sections with document metadata, ready for summarisation.
    input: Path to the policy .txt file (string) — e.g. ../data/policy-documents/policy_hr_leave.txt
    output: dict with metadata (title, department, document reference, version, effective date) and clauses — a list of {clause_number, text} in document order (1.1 through 8.2)
    error_handling: Fails loudly with a clear message if the path does not exist or the file is empty. Lines that cannot be matched to a numbered clause are collected in an unparsed list and surfaced — never silently dropped.

  - name: summarize_policy
    description: Produces a clause-complete, obligation-preserving summary from structured policy sections, with every numbered clause referenced.
    input: dict as returned by retrieve_policy (metadata + clauses list)
    output: Plain-text summary string with a metadata header and one entry per numbered clause (1.1 through 8.2), preserving binding verbs ("must", "will", "requires", "not permitted"), exact limits and dates, and ALL conditions of multi-approver clauses (e.g. 5.2 names Department Head AND HR Director). Clauses that cannot be summarised without meaning loss are quoted verbatim and flagged [FLAGGED — VERBATIM].
    error_handling: Refuses to emit the summary if any numbered clause from the source is missing from the output, or if any obligation would be softened, merged, or blended with outside knowledge. Never adds information not present in the source document.
