# skills.md — UC-X "Ask My Documents"

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy .txt files and indexes them into numbered sections
      and clauses, keyed by document filename and clause number, so any clause can be
      located and cited later. This is the sole source of truth for answering; nothing
      outside these files is ever consulted.
    input: >
      A list of file paths (strings) to the three UTF-8 policy documents:
      policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
      Defaults to the three files under ../data/policy-documents/ when none are given.
    output: >
      A structured index: an ordered list of clause records, each carrying
      doc (filename), section_number, section_title, clause_number (e.g. "3.1"), and the
      exact clause text. Retrieval-time metadata (per-clause token sets and a corpus-wide
      IDF table) is computed so lookup can rank clauses without any language model at
      runtime. No clause text is dropped, reordered, paraphrased, or invented.
    error_handling: >
      If a file is missing or unreadable, exit with a clear one-line message naming the
      file rather than silently answering from fewer documents (answering from an
      incomplete corpus would produce false refusals). A line that cannot be matched to a
      clause number is attached verbatim to the nearest preceding clause, never discarded.

  - name: answer_question
    description: >
      Answers one natural-language question strictly from the indexed documents. Returns
      either a single-source answer with a document + section citation, or the exact
      refusal template. Never blends two documents and never hedges.
    input: >
      question (str) \u2014 a free-text employee question; and the index produced by
      retrieve_documents.
    output: >
      A result object with:
        refused (bool),
        answer (str) \u2014 the cited clause text when answered, or the verbatim refusal
          template when refused,
        citation (str) \u2014 "<filename> \u00a7<clause>" when answered, empty when refused,
        reason (str) \u2014 short internal note on why it answered/refused (for the
          reviewer/log, not shown as policy content).
      When answered, every claim in `answer` is backed by the single cited clause; when
      refused, `answer` is exactly the refusal template and `citation` is empty.
    rules: >
      The best-matching clause is selected by keyword relevance (IDF-weighted term
      overlap over the clause body; action/obligation verbs such as "approve" or
      "install" are weighted highest, and multi-word terms like "leave without pay"
      are expanded to the acronyms the clauses use, e.g. "LWP"). The question is
      answered only if a single clause covers at least half of the question's content
      terms; otherwise the question is treated as not covered. If clauses from two
      different documents both clear that bar, the question is treated as
      cross-document ambiguous and refused.
      The answer is composed only from the one selected clause, with its binding verbs and
      all its conditions preserved.
    error_handling: >
      An empty or whitespace-only question returns the refusal template rather than
      raising. A question whose best clause falls below the coverage bar returns the
      refusal template (never a hedged partial answer). A question matching two documents
      returns the refusal template (never a blend). The agent never fabricates a clause
      number or a fact not present in the selected clause.
