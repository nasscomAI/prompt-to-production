skills:
  - name: retrieve_policy
    description: Load HR leave policy from text file and return content indexed by clause number and section.
    input: File path to policy_hr_leave.txt
    output: Dictionary with structure {section_number: {clause_number: clause_text, ...}, ...} — e.g. {2: {2.3: "...", 2.4: "...", ...}, 3: {3.2: "...", 3.4: "...", ...}}
    error_handling: If file missing, raise FileNotFoundError. If file cannot be parsed into numbered clauses, raise ValueError with details on which section failed.

  - name: summarize_policy
    description: Produce a structured summary of HR policy where every key clause is present with conditions intact, flagging any clause that risks meaning loss.
    input: Dictionary from retrieve_policy with full clause text indexed by section/number
    output: Text document with: (1) Section headers, (2) For each clause: clause number + one-sentence summary citing exact conditions, (3) FLAGGED CLAUSES section listing any clause quoted verbatim due to complexity, (4) VERIFICATION LIST showing which 10 key clauses were found
    error_handling: If a clause appears to have ambiguous or contradictory conditions, flag it and include verbatim quote. If a clause is missing entirely, include in VERIFICATION LIST as MISSING and do not invent text for it. Do not proceed if fewer than 8 of the 10 key clauses are found.

