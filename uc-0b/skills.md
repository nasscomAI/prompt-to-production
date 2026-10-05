skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy document and turns its numbered clauses into a
      structured, source-faithful inventory for summarization.
    input: >
      A path to a UTF-8 .txt policy file containing numbered sections and
      clauses, for example policy_hr_leave.txt.
    output: >
      Structured sections containing each section heading and every numbered
      clause with its original reference and complete source text, in document
      order.
    error_handling: >
      Report a missing, unreadable, or empty file clearly. Preserve text that
      cannot be parsed into a numbered clause as unparsed content and flag it
      for review; never fabricate clause numbers, headings, or missing text.

  - name: summarize_policy
    description: >
      Produces a concise policy summary from structured clauses while preserving
      each obligation's scope, force, and all material conditions.
    input: >
      Structured numbered sections produced by retrieve_policy, including each
      clause reference and its complete source text.
    output: >
      A text summary with one traceable entry for every numbered source clause,
      labeled with the original clause reference. Each entry preserves named
      actors, approvals, thresholds, dates, exceptions, consequences, and
      binding language; an entry may be quoted verbatim and marked for review.
    error_handling: >
      Do not summarize from incomplete or unreferenced source text. When a
      concise restatement would omit a material condition or alter the meaning,
      quote the original clause verbatim and flag it for review. Never fill gaps
      with external policy knowledge or general HR practice.
