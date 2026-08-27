# skills.md

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured numbered sections.
    input: Path to a .txt policy document.
    output: List of sections, each containing clause number and full clause text.
    error_handling: If the file is missing, empty, or unreadable, abort with an error.

  - name: summarize_policy
    description: Take structured sections and produce a compliant summary with clause references.
    input: List of structured sections from retrieve_policy.
    output: A summary text where every source clause is represented, multi-condition obligations are preserved, and no external information is added. Each clause reference must be cited.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it. If the input sections are empty or malformed, abort with an error.
