skills:
  - name: retrieve_policy
    description: Loads the raw text from the HR policy file, validates its existence, and structures it into accessible sections.
    input: File path string pointing to policy_hr_leave.txt.
    output: A string containing the full, raw text of the policy document.
    error_handling: If the file is missing or unreadable, log an error and exit gracefully without crashing.

  - name: summarize_policy
    description: Processes structured policy text using LLM rules to generate a summary that explicitly retains all 10 core clauses and multi-condition rules.
    input: Raw string content of the policy document.
    output: A comprehensive, clause-faithful plain text summary containing no scope bleed.
    error_handling: If API limits or connectivity issues occur, retry up to 3 times or fall back to an explicit failure message.