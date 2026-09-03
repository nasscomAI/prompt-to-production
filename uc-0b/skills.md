skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content parsed into structured numbered sections.
    input: File path string pointing to a .txt policy document (e.g. policy_hr_leave.txt).
    output: Ordered list of numbered sections, each containing the clause number and its full verbatim text.
    error_handling: If the file is missing or unreadable, raise a FileNotFoundError with the path. If the document contains no detectable numbered sections, return the full raw text and flag the response with NEEDS_REVIEW so the caller knows structure could not be parsed.

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a clause-complete, meaning-preserving summary with explicit clause references.
    input: Ordered list of numbered sections as returned by retrieve_policy (clause number + verbatim text per entry).
    output: Plain-text summary where every input clause is represented, each point is prefixed with its clause number, binding verbs are preserved verbatim, and any clause that cannot be summarised without meaning loss is quoted verbatim and marked NEEDS_REVIEW.
    error_handling: If a clause contains multi-condition obligations (e.g. two required approvers), all conditions must be preserved and none dropped silently; if any condition cannot be preserved faithfully, quote the clause verbatim and append NEEDS_REVIEW. If the input section list is empty, return an error stating no policy content was provided rather than generating an empty or fabricated summary.
