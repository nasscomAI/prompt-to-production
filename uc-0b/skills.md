# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a plain-text policy document (.txt).
    output: Ordered structured sections with clause numbers, clause text, and detected binding verbs.
    error_handling: If the file is missing or unreadable, return a hard error. If numbering is malformed, return best-effort sections and flag unresolved lines for review.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references and preserved obligations.
    input: Structured numbered sections from retrieve_policy.
    output: Summary entries mapped to clause references, preserving all conditions and obligations; includes verbatim quote plus flag when meaning-preserving paraphrase is not possible.
    error_handling: If a required clause is missing from inputs, return an error. If summarization risks meaning loss, quote source clause verbatim and flag it.
