# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes every numbered section by
      document filename and section number, so that any retrieved passage
      carries its provenance from the moment it is read.
    input: >
      paths : list[str] — the three files in ../data/policy-documents/
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt)
    output: >
      list of section records, each —
        document : str, the filename, e.g. "policy_it_acceptable_use.txt"
        section  : str, e.g. "3.1"
        heading  : str, the parent section heading, e.g. "PERSONAL DEVICES (BYOD)"
        text     : str, the section text verbatim with line-wrap whitespace
                   collapsed
      Provenance is attached at index time rather than reconstructed later.
      A passage that has been separated from its filename cannot be checked for
      single-source compliance, so the two are never apart.
    error_handling: >
      A missing or unreadable policy file exits non-zero naming the path — the
      system does not answer from two documents when it was configured for
      three, because a refusal computed over a partial corpus is not a
      trustworthy refusal. A file that yields zero numbered sections is
      reported as a parse failure rather than silently contributing nothing to
      the index.

  - name: answer_question
    description: >
      Scores the indexed sections against a question, selects a single winning
      document, and returns either a single-source cited answer or the refusal
      template.
    input: >
      question : str — free text from the CLI
      index    : list — the section records from retrieve_documents
    output: >
      dict —
        kind      : "ANSWER" or "REFUSAL"
        document  : str, the single source filename (empty on refusal)
        citations : list of {section, heading, text} — all from that one
                    document, never mixed
        body      : str, the text printed to the user; on refusal this is the
                    refusal template reproduced character for character
        reason    : str, why a refusal was issued — NO_MATCH or
                    CROSS_DOCUMENT_AMBIGUITY
    error_handling: >
      Refuses in preference to guessing, and the refusal paths are the
      substance of this skill rather than its edge cases. A weak match — fewer
      than two distinct content terms, or less than a third of the question's
      terms covered — is a refusal, because one incidental shared word is not
      evidence. A near-tie between two documents is a refusal, because that gap
      is exactly where a blended answer would be invented. Before returning,
      the function asserts that its citations span exactly one filename and
      that no banned hedging phrase appears in the body; either assertion
      failing converts the response into a refusal rather than emitting it. An
      empty or whitespace-only question is rejected without being scored.
