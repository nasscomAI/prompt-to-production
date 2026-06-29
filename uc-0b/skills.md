# skills.md — UC-0B Skills (Clause-Accurate)

skills:
  - name: retrieve_policy
    description: Load the HR policy .txt file and split it into numbered clause sections by finding patterns like "2.3", "2.4", etc.
    input: { path: string (file path to policy_hr_leave.txt) }
    output: { text: string, sections: dict[str, str] mapping "<major>.<minor>" -> clause text snippet }
    error_handling: If the file cannot be read, raise; if a required clause number is not found, return sections missing those keys (so the caller can mark MISSING CLAUSE).

  - name: summarize_policy
    description: Produce a clause-accurate summary for the required 10 clauses, preserving ALL conditions and refusing/quoting if clause text cannot be located.
    input: { sections: dict[str, str] }
    output: { summary_text: string }
    error_handling: If any required clause key is missing from sections, include a line "MISSING CLAUSE <number>" instead of guessing; if a clause exists, summarize using only its text and include the clause number in the summary.

