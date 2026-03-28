# skills.md
skills:
  - name: retrieve_policy
    description: Parses an incoming text file and extracts the content into structured, numbered sections.
    input: The absolute or relative path to a .txt policy document.
    output: A list of dictionaries representing individual categorized clauses, capturing the clause number and unmodified text.
    error_handling: If the file cannot be accessed or parsed, it raises a structured format error and aborts safely.

  - name: summarize_policy
    description: Compiles the structured policy sections into an exact, verbatim compliant summary representing core obligations.
    input: A list of structured dictionaries produced by retrieve_policy.
    output: A string containing the numbered clauses perfectly quoted and bulleted to guarantee no scope bleed or condition omission.
    error_handling: If a clause cannot be identified or is malformed, it flags the missing clause block as "NEEDS REVIEW".
