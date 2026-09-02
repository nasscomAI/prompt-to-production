# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes every clause by document name and section/clause number for retrieval.
    input: no arguments — reads the fixed document set from ../data/policy-documents/ (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: list of indexed units, each with document (filename), section (e.g. "3.1"), title (section heading) and text (verbatim clause text, whitespace-normalised).
    error_handling: a missing document file prints a warning naming the file and continues with the remaining documents; empty documents produce an empty index rather than an error; malformed clause lines are attached to the previous clause as continuation text so nothing is silently lost.

  - name: answer_question
    description: Scores indexed clauses against the question terms (IDF-weighted, occurrence-capped, section titles at half weight, plus a curated concept-boost table for unambiguous intents like BYOD/install/carry-forward/LWP) and returns a single-source cited answer, or the exact refusal template when the question is not covered or evidence is split across documents.
    input: a question string from the user (interactive prompt or --question argument).
    output: either "<best clause text> [Source: <document>, section <number>]" from exactly one document, or the refusal template verbatim with [relevant team] resolved to the best-matching document's department (HR / IT / Finance) or "the relevant policy owner" when nothing matches.
    error_handling: empty question → re-prompt; fewer than 2 distinct content-term matches in the best clause (and no concept boost) → refusal template; top two clauses from different documents with equal scores → refusal template (cross-document ambiguity is refused, never blended); no hedging phrases are ever emitted.
