skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and returns its content as ordered, structured numbered sections and clauses.
    input: A path to a UTF-8 .txt policy file.
    output: The document metadata when present and an ordered list of sections, each containing its heading and every numbered clause with its original clause reference and complete text.
    error_handling: Reject a missing, unreadable, non-.txt, or empty file with a clear error and no partial result. Preserve malformed or ambiguous clause text for review; do not repair, infer, or renumber it.

  - name: summarize_policy
    description: Produces a source-faithful summary from structured policy sections while retaining clause references and all material obligations and conditions.
    input: Ordered structured sections from retrieve_policy, where each clause has an original reference and complete source text.
    output: An ordered summary containing every input clause exactly once, identified by its original clause reference. Entries preserve binding language, actors, approvals, thresholds, dates, deadlines, exceptions, and consequences; entries that cannot be condensed faithfully are quoted verbatim and prefixed with [VERBATIM - MEANING LOSS].
    error_handling: Reject input with missing clause references or text, duplicate references, or an unknown ordering. Do not add external information. If a clause's meaning cannot be determined from its supplied text, preserve it verbatim with the meaning-loss label rather than guessing.
