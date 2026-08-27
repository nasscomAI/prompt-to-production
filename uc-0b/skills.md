skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, explicitly numbered sections.
    input: File path string pointing to a valid .txt document format (e.g., policy_hr_leave.txt).
    output: A structured list or array representing individual numbered clauses and their verbatim content.
    error_handling: Return a parsing failure error if the file is unreadable, empty, or lacks discernible numbered sections instead of returning unformatted text.

  - name: summarize_policy
    description: Takes structured policy sections and produces a fully compliant summary with explicit clause references.
    input: A structured list or dictionary containing the original, numbered policy clauses.
    output: A precise text summary mapping directly back to the provided clauses with zero condition-drops or scope loss.
    error_handling: If a clause contains ambiguous or complex logic that resists summarization, quote the policy verbatim and append a "[FLAG: Verbatim]" warning rather than attempting to soften the meaning.
