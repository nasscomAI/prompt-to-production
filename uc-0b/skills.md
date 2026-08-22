# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy document text file and parses it into structured numbered sections, preserving clause numbers, section headings, and all text content exactly as written.
    input: File path (string) pointing to a .txt policy document with numbered clauses (e.g., '../data/policy-documents/policy_hr_leave.txt').
    output: Dictionary or structured object with keys for each section heading and nested dictionary of clause numbers mapped to their full text content. Preserves all formatting, binding verbs, and multi-condition phrases exactly as they appear in source.
    error_handling: If file not found, print clear error with file path and exit. If file is empty, return empty structure and log warning. If clause numbering is malformed or inconsistent, preserve original text and flag parsing issues but do not crash. Never invent or normalize clause content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary text that preserves all numbered clauses, multi-condition obligations, and binding language without adding external information or softening requirements.
    input: Structured policy content (dictionary/object) with section headings and clause numbers mapped to full text, as produced by retrieve_policy.
    output: Plain text summary string written to output file path. Summary must include: all clause numbers from source, all multi-condition requirements preserved, all binding verbs unchanged, no scope bleed phrases, flagged verbatim quotes where summarization risks meaning loss.
    error_handling: If a clause contains multiple conditions and ambiguity exists about which to preserve, include all conditions and flag for review. If binding language is unclear (e.g., mixed 'may' and 'must' in same clause), preserve exact source wording and flag: [BINDING LANGUAGE UNCLEAR]. If output file path is invalid, print error and exit. If no clauses are present in input, refuse to generate summary and explain that source document has no numbered clauses to summarize.
