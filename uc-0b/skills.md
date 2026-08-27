# skills.md

skills:
  - name: retrieve_policy
    description: Opens and reads a raw textual policy file and parses its contents into structured, numbered sections.
    input: The file path to a text document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured array or dictionary of text blocks, strictly keyed by their respective clause numbers.
    error_handling: If the file is missing, completely empty, or lacks readable numbered sections, raise a parsing error immediately and halt.

  - name: summarize_policy
    description: Receives the parsed policy sections and generates a highly accurate, compliant summary that preserves every original clause and multi-part condition.
    input: Structured policy sections (an array or dictionary of text blocks with clause numbers).
    output: A formatted string document (e.g., summary_hr_leave.txt) containing the summary with explicit references to every clause.
    error_handling: If standard summarization risks softening the obligation or dropping a condition, revert to quoting the entire section verbatim and append a specific "[REVIEW_FLAG]".
