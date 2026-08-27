# skills.md
# Skill definitions for UC-0B: Policy Document Summarizer

skills:
  retrieve_policy:
    description: >
      Loads a .txt policy file from the given input path and returns its content
      as structured numbered sections.
    inputs:
      - input_path: string — path to the policy .txt file
    outputs:
      - sections: list — each item is a dict with keys {clause_id, heading, body}
    behaviour: >
      Read the file line by line. Detect clause numbers (e.g., "2.3", "5.2") as section delimiters.
      Preserve original text faithfully — do not paraphrase or alter during retrieval.
      If the file is missing or empty, raise a clear error and stop.

  summarize_policy:
    description: >
      Takes the structured sections from retrieve_policy and produces a compliant
      plain-text summary that preserves every binding obligation.
    inputs:
      - sections: list — structured sections from retrieve_policy
    outputs:
      - summary: string — the final summary text
    behaviour: >
      For each section, produce a concise summary that retains:
        - The clause number
        - The core obligation (using the original binding verb: must, requires, will, etc.)
        - All conditions attached to the obligation (never drop conditions silently)
      If a clause cannot be summarised without meaning loss, quote it verbatim
      and prefix with [VERBATIM].
      Never add external knowledge, assumptions, or scope bleed.
      Validate that all 10 required clauses are present before outputting.
