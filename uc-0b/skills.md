# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content as structured numbered sections.
    input: >
      File path (string) pointing to a plain-text policy document.
    output: >
      A list of structured sections, each containing:
      - section_number (string): The clause/section identifier (e.g., "2.3", "5.2")
      - section_title (string): The heading or topic of the section (if present)
      - section_body (string): The full text content of that clause
    error_handling: >
      If the file path does not exist, is unreadable, or the file is empty,
      return an error object with a descriptive message and do not proceed to
      summarization. If the file does not contain recognizable numbered sections,
      return the raw content with a warning flag indicating structure could not
      be parsed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clause references, binding verbs, and multi-condition obligations.
    input: >
      A list of structured sections (as produced by retrieve_policy), each with
      section_number, section_title, and section_body.
    output: >
      A plain-text summary where each entry:
      - Starts with the clause reference (e.g., "Clause 2.3:")
      - Preserves the binding verb exactly as stated in the source
      - Retains ALL conditions for multi-condition obligations
      - Contains no added information beyond the source document
      - Flags any verbatim-quoted clause with [VERBATIM — lossy summarization risk]
    error_handling: >
      If any section_body is empty or contains ambiguous language that cannot be
      faithfully summarized, quote the original text verbatim and flag it rather
      than attempting a lossy paraphrase. If the input list is empty, refuse to
      produce output and return an error stating no sections were provided.
