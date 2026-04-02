# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of
      numbered sections, each identified by its section number and heading.
    input: >
      file_path (str) — absolute or relative path to a .txt policy document
    output: >
      list of dicts, each with keys:
        section_id (str) — e.g. "2.3", "5.2"
        heading (str) — section title if present, else blank
        text (str) — full text of the section/clause
      Also returns raw_text (str) — full file content for reference.
    error_handling: >
      FileNotFoundError: exits with descriptive message naming the missing file.
      Empty file: exits with message "Policy file is empty — cannot summarise."
      Encoding errors: retries with latin-1 before raising.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces
      a clause-complete, obligation-preserving summary with section references.
    input: >
      sections (list of dicts) — output of retrieve_policy
      required_clauses (list of str) — clause IDs that MUST appear in the summary
        e.g. ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    output: >
      summary_text (str) — formatted summary written to output file
      Each clause appears as: "[Clause X.X] <summary text>"
      Multi-condition clauses include all conditions explicitly.
    error_handling: >
      If a required clause is not found in sections, writes:
        "[Clause X.X — NOT FOUND IN SOURCE: manual review required]"
      Never silently omits a required clause.
