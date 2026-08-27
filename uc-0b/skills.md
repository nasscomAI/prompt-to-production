skills:
  - name: retrieve_policy
    description: Loads the .txt policy file from the input path and returns its content as structured numbered sections corresponding to each clause.
    input:
      type: string
      format: File path to a .txt policy document (e.g. ../data/policy-documents/policy_hr_leave.txt)
    output:
      type: object
      format: A structured mapping of clause numbers (e.g. "2.3", "2.4", "5.2") to their corresponding section text, preserving original wording and ordering as found in the source document
    error_handling:
      - If the file path does not exist or is not a .txt file, return an error indicating the input file could not be found or read, and do not proceed to summarize_policy.
      - If the file is empty or contains no identifiable numbered clauses, return an error indicating no structured sections could be extracted, rather than returning an empty or fabricated structure.
      - If a clause appears malformed or its numbering is ambiguous, preserve the raw text under a best-guess clause identifier and flag it as ambiguous rather than discarding or merging it with another clause.
      - Never alter, paraphrase, or omit any portion of the source text during retrieval; retrieval must be a faithful structural mapping only.

  - name: summarize_policy
    description: Takes structured numbered sections from retrieve_policy and produces a compliant summary with clause references that preserves every clause, all multi-condition obligations, and original binding-verb strength.
    input:
      type: object
      format: A structured mapping of clause numbers (e.g. "2.3", "2.4", "5.2") to their corresponding section text, as returned by retrieve_policy
    output:
      type: string
      format: Plain text summary written to uc-0b/summary_hr_leave.txt, organized by clause number, with each clause's obligation and binding verb strength preserved, and any verbatim-quoted clauses explicitly flagged
    error_handling:
      - If any clause from the input structured sections is missing from the generated summary, regenerate the summary to include the missing clause rather than emitting an incomplete output (addresses clause omission failure mode).
      - If a multi-condition obligation (e.g. clause 5.2's requirement for both Department Head AND HR Director approval) would have any condition dropped, retain all conditions explicitly rather than collapsing them into a single generic condition (addresses condition-drop failure mode).
      - If a binding verb would be softened (e.g. "requires" or "must" rendered as "should" or "is encouraged"), correct it to match the original binding strength from the source clause (addresses obligation softening failure mode).
      - If the summarization process would introduce content not present in the source sections (e.g. phrases like "as is standard practice" or "typically in government organisations"), remove such content before output (addresses scope bleed failure mode).
      - If a clause cannot be condensed without meaning loss, output that clause's text verbatim and prepend a flag (e.g. "[VERBATIM]") indicating it was quoted rather than summarized.
      - If the input structured sections are empty or malformed, do not produce a summary; return an error indicating retrieve_policy must be run successfully first.