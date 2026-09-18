# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to a .txt policy file, e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: A mapping of clause numbers to their exact text, e.g. {2.3: "Employees must submit...", 2.4: "Leave applications must..."}, preserving the source wording.
    error_handling: If the file is missing or unreadable, returns an error and produces no summary.

  - name: summarize_policy
    description: Takes the structured sections and produces a clause-complete plain-text summary that preserves every binding obligation and condition.
    input: Structured numbered sections (from retrieve_policy) and the coverage checklist of ten ground-truth clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    output: A plain-text summary in which each obligation is prefixed by its clause number, the binding verb is unchanged, and every multi-condition clause retains all its conditions; clauses that cannot be summarized without meaning loss are quoted verbatim and flagged NEEDS_REVIEW.
    error_handling: If a clause is missing from the input or cannot be summarized without meaning loss, quotes it verbatim and flags it NEEDS_REVIEW instead of paraphrasing.
