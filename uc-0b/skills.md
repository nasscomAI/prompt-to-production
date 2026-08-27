skills:
  - name: section_parser
    description: Splits the policy document into sections using ALL-CAPS headings or numbered patterns.
    input: Raw policy text as a string.
    output: List of (heading, body) tuples in source order.
    error_handling: If no headings found, treats entire document as one section labelled PREAMBLE.

  - name: clause_completeness_enforcer
    description: Counts all numbered and lettered clauses and verifies every one appears in the summary output.
    input: Original policy text and summarised output text.
    output: Clause count report — total found vs total summarised, with REVIEW REQUIRED if mismatch.
    error_handling: If clause count mismatches, appends warning to output file and prints to console.

  - name: meaning_preservation_checker
    description: Detects and flags clauses with vague or discretionary language that could be misread.
    input: Individual clause text as a string.
    output: Clause prefixed with [AMBIGUOUS] if it contains shall be determined / as appropriate / at discretion, else unchanged.
    error_handling: If clause is empty or whitespace-only, skip silently.

  - name: audit_trail_writer
    description: Writes generation date and clause coverage stats to the top and bottom of the summary file.
    input: Summary lines list, total clause count, summarised clause count.
    output: summary_hr_leave.txt with header and footer appended.
    error_handling: If output directory does not exist, raise FileNotFoundError before writing.
