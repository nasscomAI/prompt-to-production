# skills.md — UC-0B Policy Compliance Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured sections or clauses based on numbering.
    input: Absolute or relative path to a policy text file (e.g., `policy_hr_leave.txt`).
    output: A dictionary where keys are clause numbers (e.g., "5.2") and values are literal section texts.
    error_handling: Raises FileNotFoundError if the file is missing; handles encoding issues gracefully.

  - name: summarize_policy
    description: Generates a compliant summary of specific mandatory clauses while preserving all core conditions and avoiding scope bleed.
    input: Dictionary of policy sections and a list of target clause numbers.
    output: A formatted multi-line string containing the summaries of 10 mandatory clauses (2.3–7.2).
    error_handling: Flags missing clauses or complex sections that require verbatim quoting/NEEDS_REVIEW.