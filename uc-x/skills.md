# skills.md — UC-X Policy Question Answering

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files and indexes every numbered clause by
      document filename and section number, keeping the clause text verbatim.
    input: >
      directory (str) — path to the folder holding policy_hr_leave.txt,
      policy_it_acceptable_use.txt and policy_finance_reimbursement.txt.
    output: >
      dict:
        documents — {filename: {reference, title, clauses}} where each clause is
                    {id: "3.1", section: "3", section_title: str, text: str,
                     document: filename}
        clauses   — flat list of every clause across all three documents, each
                    carrying its own document filename so a clause can never be
                    quoted without knowing its source
      Clause text has hard line wraps rejoined and is otherwise untouched, so
      every quotation is a literal substring of the source file.
    error_handling: >
      A missing or unreadable file -> named on stderr and exit 1; the agent will
      not answer from two documents while claiming three, because the refusal
      template names all three by filename. A document that parses to zero
      clauses -> exit 1. Files other than the three expected names are ignored
      rather than silently indexed.

  - name: answer_question
    description: >
      Scores the question against every clause, selects ONE source document,
      and returns either verbatim cited clauses from that document alone or the
      exact refusal template.
    input: >
      index (dict) — from retrieve_documents
      question (str) — free text
    output: >
      dict:
        kind      — "answer" or "refusal"
        document  — the single source filename, or "" for a refusal
        citations — list of {citation, text} where citation is
                    "policy_it_acceptable_use.txt § 3.1"; empty for a refusal
        body      — the printable response: cited quotations, or the refusal
                    template character for character
        diagnostic— why this document won or why the agent refused. Printed
                    OUTSIDE the answer block and labelled, so the refusal
                    template is never altered.
      Term matching treats two words as the same when their common prefix is at
      least min(len(a), len(b), 5) characters, so "approves" reaches "approval"
      and "use" reaches "used", while "day" does not reach "data".
    error_handling: >
      Refuses in four distinct situations, all returning the identical template:
      no clause matched at all; the best clause matched fewer than 2 distinct
      question terms; the winning document failed to beat the runner-up by 1.25x
      (genuine cross-document ambiguity); or the assembled response failed its
      own single-source or hedging check. The last case means a bug was caught
      at runtime — the agent refuses rather than emitting a response it could
      not verify, and reports the failure on stderr.
