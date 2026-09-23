skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses the content into structured numbered sections and individual clauses.
    input: input_path (str path to policy .txt file)
    output: dict mapping section headings and clause numbers to their exact verbatim text content
    error_handling: Raises FileNotFoundError if input path is invalid; flags malformed or unnumbered sections gracefully.

  - name: summarize_policy
    description: Processes structured policy sections into an obligation-preserving summary with verified clause references and exact condition preservation.
    input: dict of structured policy sections and clauses
    output: str representing the complete formatted summary text with clause numbers and preserved obligations
    error_handling: If a clause contains complex multi-condition rules that cannot be abbreviated without meaning loss, quotes it verbatim and tags it.
