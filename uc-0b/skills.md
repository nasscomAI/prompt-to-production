# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed into structured numbered sections.
    input: File path (str) pointing to a plain-text policy document (e.g. policy_hr_leave.txt).
    output: Ordered list of section objects, each containing a clause/section number and its full text.
    error_handling: If the file is missing or unreadable, raise a descriptive FileNotFoundError. If a section number cannot be parsed, include the raw text block with a [PARSE WARNING] tag and continue loading remaining sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-faithful summary with inline clause references, preserving all binding conditions and obligations.
    input: Ordered list of section objects returned by retrieve_policy.
    output: Plain-text summary where each clause is referenced by its number, binding verbs are preserved, and multi-condition obligations list all conditions explicitly.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and append [VERBATIM — meaning loss risk]. Never silently drop a clause or condition; if a section is ambiguous, flag it with [NEEDS REVIEW] and include the original text.
