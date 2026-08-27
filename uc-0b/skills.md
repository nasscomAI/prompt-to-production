# skills.md

skills:
  - name: retrieve_policy
    description: Loads a structured .txt policy file and returns its content mapped into structured numbered sections.
    input: File path to a raw text policy document (e.g., policy_hr_leave.txt).
    output: A dictionary or object mapping clause numbers (e.g., '2.3', '5.2') to their full verbatim text strings.
    error_handling: Check if the file exists and is readable. If parsing fails to find numbered clauses, raise an error indicating the document structure is unsupported or malformed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant, point-by-point summary preserving all conditions and obligations.
    input: A dictionary of numbered policy clauses (output from retrieve_policy).
    output: A single string or document containing the summary, ensuring every numbered clause is referenced and all conditions (like multiple approvers) are explicitly stated without softening binding verbs.
    error_handling: If a clause cannot be summarized without risking the loss of a condition or meaning, quote it verbatim and prefix/flag it with "[VERBATIM]". Ensure no external knowledge or unverified practices are injected; if uncertain, fall back to verbatim quote.
