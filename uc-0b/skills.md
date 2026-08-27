# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: extract_clauses
    description: Parse policy document and extract all numbered clauses with their hierarchical structure and binding obligations.
    input: Path to policy document text file.
    output: List of tuples (clause_number, full_text, binding_verb) for each clause found.
    error_handling: If document is empty or has no numbered clauses, return empty list. If clause parsing fails, skip malformed clauses and continue with well-formed ones.

  - name: preserve_multi_conditions
    description: Identify and preserve multi-condition obligations (e.g., requiring approval from multiple entities) without dropping conditions.
    input: Clause text and binding verb.
    output: String that includes all conditions separated with AND, e.g., "requires X AND Y".
    error_handling: If conditions are ambiguous, preserve all entities/conditions found in the text. If no conditions found, return the clause as-is.

  - name: generate_summary
    description: Combine extracted clauses into a readable summary preserving all clauses and conditions without alteration.
    input: List of clauses with their conditions and binding verbs.
    output: Summary text structured by numbering, with all clauses and conditions preserved.
    error_handling: If input clause list is empty, output "No clauses found in document." If clause numbering is non-standard, preserve the numbering as-is.
