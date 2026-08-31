# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy text file and returns its content as structured numbered sections.
    input: A path to a .txt policy document.
    output: A list of numbered policy sections containing clause references and source text.
    error_handling: Reject missing or unreadable files and do not substitute external information.

  - name: summarize_policy
    description: Produces a compliant clause-referenced summary while preserving all conditions and obligations.
    input: Structured numbered policy sections.
    output: A summary containing every required clause with its original obligation and conditions preserved.
    error_handling: If a clause cannot be safely summarized without losing meaning, include it verbatim and flag it for review.
