# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured, numbered policy sections.
    input: File path to policy .txt file (input_path).
    output: List of section dictionaries containing section_number, title, and body text.
    error_handling: Raises file not found or invalid format error if text file cannot be parsed into numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and generates a complete, non-lossy summary referencing every clause number and preserving all binding obligations.
    input: List of structured policy section dictionaries.
    output: Plain text summary string containing section-by-section summaries with explicit clause citations.
    error_handling: If dual approval or binding verbs are ambiguous in a section, quotes the section verbatim and flags for review.
