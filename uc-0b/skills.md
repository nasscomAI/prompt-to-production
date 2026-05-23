# skills.md

skills:
  - name: retrieve_policy
    description: Loads a raw policy text file from the filesystem and parses it into structured numbered sections.
    input: Path to the policy text file (String).
    output: Structured representation of the policy (Dictionary/JSON mapping section and clause headers to their raw text contents).
    error_handling: Raises a FileNotFoundError or ValueError if the file path is invalid, the file is empty, or the policy format is unparseable.

  - name: summarize_policy
    description: Extracts and maps the ten core policy clauses to a high-fidelity, precise summary that strictly preserves all binding verbs and multi-condition obligations.
    input: Structured policy sections (Dictionary/JSON) and a list of target clause numbers (Array of Strings).
    output: A precise, high-fidelity summary text file preserving all binding obligations, with verbatim quotes and warning flags for any clauses that cannot be safely summarized without meaning loss (String).
    error_handling: Raises a ValueError or validation exception and refuses to proceed if any of the ten target clauses are missing from the input, or if there is insufficient information to resolve their conditions.
