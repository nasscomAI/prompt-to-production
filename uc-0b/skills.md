skills:
  - name: retrieve_policy
    description: >
      Loads the HR leave policy text file from disk and parses it into
      structured numbered sections, preserving each clause's number and
      full text exactly as written in the source document.
    input:
      type: file_path
      format: >
        A string path to a .txt file (e.g. "../data/policy-documents/policy_hr_leave.txt").
        The file is expected to contain numbered clauses (e.g. "2.3", "5.2")
        with associated body text.
    output:
      type: structured_sections
      format: >
        A list of objects, each with fields: clause_number (e.g. "2.3"),
        clause_text (verbatim text of that clause). Order matches the
        order clauses appear in the source document.
    error_handling: >
      If the file path does not exist or cannot be read, raise a clear
      error and halt — do not proceed to summarization with partial or
      missing content. If a clause number cannot be confidently parsed
      (e.g. malformed numbering, ambiguous section breaks), flag that
      section as "unparsed" rather than silently dropping it or guessing
      its clause number. Never fabricate clause content to fill a gap.

  - name: summarize_policy
    description: >
      Takes the structured clause sections from retrieve_policy and
      produces a condensed summary that preserves every clause's binding
      obligations, all multi-part conditions, and explicit clause number
      references, without adding information not present in the source.
    input:
      type: structured_sections
      format: >
        The list of clause_number/clause_text objects produced by
        retrieve_policy.
    output:
      type: text_summary
      format: >
        Plain text summary, organized by clause number, where each
        clause's summary line begins with its clause number (e.g.
        "2.3: ..."), and clauses with multiple conditions list every
        condition, not just one representative condition.
    error_handling: >
      If a clause cannot be condensed without losing meaning (per the
      README's stated failure modes — clause omission, scope bleed,
      condition dropping), the skill must output that clause's text
      verbatim with a flag (e.g. "[VERBATIM - meaning loss risk]")
      instead of producing a lossy paraphrase. If any clause from the
      input is missing from the output, this is treated as a critical
      failure — the skill must not silently omit a clause under any
      circumstance. If input contains an "unparsed" section from
      retrieve_policy, that section must also appear verbatim and
      flagged, never dropped.