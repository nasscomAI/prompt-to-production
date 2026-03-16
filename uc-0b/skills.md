# skills.md — UC-0B Policy Summarizer
skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections.
    input: File path to the .txt policy document.
    output: List of objects, each containing clause number and raw text.
    error_handling: Refuse to process if the file format is not .txt or if numbered sections cannot be reliably parsed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a summary that adheres to all enforcement rules.
    input: Structured policy sections (List of objects).
    output: A summary string with explicit clause references and flags for high-fidelity needs.
    error_handling: Flags sections for manual review if they contain complex multi-condition logic that risks meaning loss during summarization.
