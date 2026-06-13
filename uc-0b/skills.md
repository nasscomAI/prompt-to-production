# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content as structured numbered sections preserving clause numbers and hierarchy.
    input: String path to a .txt policy file.
    output: List of structured sections, each containing clause number, heading, and full text body.
    error_handling: If the file path is invalid, missing, or not a .txt file, return an error with the exact path that failed and do not proceed to summarization. If the file is empty or contains no identifiable numbered clauses, return a warning and the raw text as a single unstructured block.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary that preserves every clause, all multi-condition obligations, and original binding verbs without adding information not in the source.
    input: List of structured sections as returned by retrieve_policy.
    output: Plain-text summary with explicit clause references where each numbered clause is present, all conditions within multi-condition obligations are retained, and binding verbs match the source document.
    error_handling: If any clause cannot be summarised without meaning loss, quote it verbatim and flag it with a VERBATIM marker. If input sections are empty or malformed, return an error and do not produce a partial summary. If scope bleed is detected (language not present in the source such as "as is standard practice" or "typically"), strip it and flag the affected clause for review.
