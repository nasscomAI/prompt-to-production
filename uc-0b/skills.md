# skills.md — UC-0B HR Leave Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as an ordered list of numbered sections. Each section contains its heading and all its sub-clauses as verbatim text, preserving clause numbers, binding verbs, and numeric values exactly as written.
    input: A file-path string pointing to the policy .txt file.
    output: A list of dicts, one per section, each with keys — section_number (str), heading (str), clauses (list of dicts with keys clause_number (str) and text (str)).
    error_handling: If the file is not found, print a clear error to stderr and exit with a non-zero status code. If the file cannot be parsed into sections, return the entire text as a single section labelled "1" with heading "Full Document" so that summarise_policy can still process it. Never raise an unhandled exception.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and writes a clause-faithful, plain-language summary to an output .txt file. Every numbered clause must appear in the summary. Multi-condition obligations must preserve all conditions. Binding verbs must not be softened. No external information may be added.
    input: Two arguments — sections (list of dicts as returned by retrieve_policy) and output_path (str, path to write the summary .txt file).
    output: A .txt file at output_path containing the complete structured summary, organised by section, with clause references (e.g. "2.3", "5.2") retained in the summary text. Any clause quoted verbatim due to condition sensitivity must be marked [VERBATIM — condition-sensitive].
    error_handling: If a section or clause dict is missing expected keys, log a warning to stderr identifying the section number and continue processing remaining sections — do not crash. If the output file cannot be written, print a clear error to stderr and exit with a non-zero status code.
