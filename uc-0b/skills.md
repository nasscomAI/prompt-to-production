# skills.md
# UC-0B Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Loads a structured .txt policy document and returns the content as segmented numbered clauses for accurate tracing.
    input: File path (string) referencing the physical .txt policy file.
    output: A dictionary mapping numerical clause IDs (e.g. "2.3") to exact verbatim string content.
    error_handling: Raises FileNotFoundError if missing. If file lacks numbering, falls back to newline-based paragraph segmentation.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant, meaning-preserved summary maintaining multi-conditional obligations and specific binding verbs.
    input: Dictionary of segmented clauses and strict rule constraints.
    output: Formatted string containing the final strictly summarized policy with direct clause references.
    error_handling: If a clause cannot be compressed without risking semantic or condition loss, quotes the clause verbatim and flags it.
