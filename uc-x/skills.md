# skills.md — UC-X Policy Q&A

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for single-source lookup.
    input: A directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: An index mapping (document name, section number) to section text, plus the list of documents loaded.
    error_handling: Refuses with a clear error when any of the 3 files is missing or contains no numbered sections; never answers from a partial index without reporting what is missing.

  - name: answer_question
    description: Routes one question to the single best-matching document section and returns a cited answer or the exact refusal template.
    input: A question string plus the document index from retrieve_documents.
    output: Either a single-source answer with [document, section] citations on every factual claim, or the refusal template reproduced exactly.
    error_handling: Returns the refusal template (never a guess) when no intent matches or the match spans documents; fails its self-check rather than emitting hedging phrases or multi-document blends.
