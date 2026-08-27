skills:
  - name: retrieve_policy
    description: Load a policy text document and parse its content into structured numbered sections for easier analysis.
    input: input_path (str to the source text file).
    output: A collection (e.g., list of dicts) containing section headers, clause numbers, and the raw text content of each section/clause.
    error_handling: Raise an FileNotFoundError if the input file does not exist. If the document structure is malformed, split by generic paragraphs or numbered markers.

  - name: summarize_policy
    description: Summarize structured policy sections, ensuring that all 10 critical clauses are explicitly preserved and that multi-condition constraints are fully detailed without obligation softening or scope bleed.
    input: structured_clauses (collection of parsed policy sections).
    output: A summarized text string where each critical clause is represented alongside its clause reference, quoting verbatim and flagging any clause where summary risks meaning loss.
    error_handling: If a critical clause is missing from the structured input, log a warning and copy the missing clause structure as an empty obligation with a warning flag.
