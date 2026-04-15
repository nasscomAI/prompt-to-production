# skills.md — UC-0B

skills:
  - name: retrieve_policy
    description: Reads the raw txt policy file from the given file path.
    input: File path string pointing to the policy document (e.g. `../data/policy-documents/policy_hr_leave.txt`).
    output: Raw string containing the text of the policy document.
    error_handling: Raises FileNotFoundError if the file doesn't exist.

  - name: summarize_policy
    description: Invokes the Gemini LLM with the raw policy text and the strict system rules from agents.md to produce a highly accurate summary.
    input: Raw text string of the policy document.
    output: A string containing the compliant summary.
    error_handling: Handles API rate limits or errors, and outputs a fallback error message if generation fails.
