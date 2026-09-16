skills:
  - name: retrieve_policy
    description: Load the supplied plain-text policy file and expose its numbered clauses as structured source material.
    input: A path to a UTF-8 `.txt` policy file.
    output: An ordered structured collection of sections, with each section containing its clause number and verbatim source text.
    error_handling: If the path is missing, unreadable, not a text file, or contains no identifiable numbered clauses, report the error and do not invent or repair policy content. Preserve ambiguous clause text verbatim and flag it for review.

  - name: summarize_policy
    description: Produce a source-grounded summary of structured policy sections without changing their meaning.
    input: The ordered structured sections returned by `retrieve_policy`, including clause numbers and verbatim text.
    output: A concise summary organized by clause reference, containing every numbered clause and preserving every obligation, condition, threshold, deadline, exception, required approver, and consequence.
    error_handling: If sections are missing, malformed, duplicated, or ambiguous, stop and report the issue rather than guessing. If a clause cannot be paraphrased without meaning loss, quote it verbatim and explicitly flag it for review. Add no information from outside the source.
