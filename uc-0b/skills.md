# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and parses it into structured numbered clauses with their parent section headings.
    input: str path to policy_hr_leave.txt (UTF-8/ASCII plain text with numbered x.y clauses).
    output: dict mapping clause id (e.g. "2.3") to its full clause text, plus ordered list of section headings.
    error_handling: Missing/unreadable file exits non-zero with a clear message; zero parsed clauses aborts the run rather than emitting an empty summary.

  - name: summarize_policy
    description: Produces a compliant summary in which every numbered clause is present, referenced, and condition-complete — paraphrasing only when safe, quoting verbatim when not.
    input: structured clauses from retrieve_policy (dict of id → text) plus section headings.
    output: str summary document (written to summary_hr_leave.txt) listing each clause as "[x.y] summary line", verbatim quotes flagged [VERBATIM QUOTE] for multi-condition clauses, and a coverage footer.
    error_handling: Unknown clause ids absent from the curated faithful-summary table are quoted verbatim and flagged instead of dropped or improvised; a built-in self-check verifies clause coverage, trap-clause conditions (e.g. 5.2 both approvers), and absence of scope-bleed phrases, reporting PASS/FAIL per check.
