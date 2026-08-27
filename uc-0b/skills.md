# skills.md — UC-0B Policy Summarization

skills:
  - name: retrieve_policy
    description: Loads a policy document text file and returns its content as structured numbered sections preserving original formatting and clause numbering.
    input: File path (string) to a .txt policy document with numbered sections and clauses.
    output: Dictionary with keys for document metadata (title, reference number, version, effective date) and 'sections' containing list of section objects, each with section number, title, and list of clause objects (clause number and text). Returns structured representation preserving all original clause numbers.
    error_handling: If file does not exist, raises FileNotFoundError with clear message. If file is not readable or empty, raises ValueError. If file does not contain recognizable section/clause structure (no numbered clauses found), raises ValueError indicating malformed policy document. Does not attempt to parse non-text formats.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all clauses, conditions, and binding obligations with clause references.
    input: Structured policy document (dictionary format from retrieve_policy) containing sections and clauses with their numbers and text.
    output: String containing the summary text with each clause represented, all conditions preserved, binding verbs intact, and clause references in format "Section X.X requires/states...". Includes [VERBATIM: X.X] flags for clauses quoted verbatim. Returns summary text suitable for writing to output file.
    error_handling: If input structure is missing required fields (sections or clauses), raises ValueError. If a clause contains ambiguous or complex conditional logic that cannot be reliably summarized without meaning loss, quotes it verbatim with [VERBATIM] flag rather than attempting lossy paraphrase. Validates that summary includes reference to every clause number from input - if any clause would be omitted, raises ValueError with list of missing clause numbers before returning summary.
