# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files and builds a searchable index of their
      numbered sections, keyed by document filename and section number, with
      an acronym glossary derived from the documents themselves.
    input: >
      doc_dir (str) — path to data/policy-documents/ containing
      policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A dict with keys: sections (list of {doc, number, heading, text,
      tokens}), documents (list of filenames actually loaded), aliases (dict
      mapping acronym -> expansion, harvested from 'Expansion (ACRONYM)'
      patterns in the source), and idf (dict token -> inverse document
      frequency across sections, used to weight rare terms above common ones
      like "policy" or "employee").
    error_handling: >
      A missing policy file: named explicitly at startup and excluded from the
      index; the refusal template is rebuilt to list only the documents
      actually available, so it never claims coverage the index does not have.
      All three files missing: exits rather than starting a session that would
      refuse every question for the wrong reason.
      A file that parses to zero numbered sections: reported and excluded, so
      an unparsed document cannot silently reduce the corpus while the agent
      still advertises it.
      Acronym pattern matching an ordinary parenthetical: the alias is only
      accepted when the parenthesised token is 2-5 uppercase characters and
      the preceding words supply matching initials, so "(CMC)" is harvested
      and "(January-March)" is not.

  - name: answer_question
    description: >
      Answers one question from a single document's numbered sections with
      citations, or returns the refusal template verbatim.
    input: >
      index (dict from retrieve_documents), question (str, free text typed by
      the user at the CLI).
    output: >
      A dict with keys: mode ("answer" or "refusal"), document (filename or
      None), sections (list of cited section numbers), text (the printed
      response), and diagnostics (per-document scores and the margin between
      the top two, so the routing decision is inspectable). In "answer" mode
      text contains only sentences drawn from the cited sections of one
      document.
    error_handling: >
      Empty or whitespace-only question: re-prompts rather than scoring an
      empty token set, which would otherwise match everything equally and
      produce an arbitrary document.
      No document reaching the relevance threshold (hallucination failure
      mode): returns the refusal template. Absence of a match is reported as
      absence, never filled from the agent's own knowledge.
      Two documents within the ambiguity margin (cross-document blending
      failure mode): returns the refusal template rather than selecting the
      marginally higher score. An arbitrary pick between two plausible sources
      is treated as the same error as merging them.
      A drafted answer containing any banned hedging phrase (hedged
      hallucination failure mode): the draft is discarded and replaced with
      the refusal template. The check runs on the final string, after
      assembly, so it cannot be bypassed by how the answer was built.
      A candidate sentence with no section number attached: dropped before
      printing, because an uncited sentence is indistinguishable from
      invention.
      Question matching sections in one document only, but weakly: still
      subject to the relevance threshold — a weak single-source match is a
      refusal, not a low-confidence answer.
