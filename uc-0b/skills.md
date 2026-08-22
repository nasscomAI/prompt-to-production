skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document (string).
    output: A list of section dictionaries, each containing section_number (e.g. "2.3"), section_heading (e.g. "ANNUAL LEAVE"), and section_text (the full text of that clause).
    error_handling: If the file does not exist, is empty, or cannot be parsed into numbered sections, return an error object with message "ERROR: Input is not a valid policy document. No summary produced." Do not attempt to guess or fabricate content.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary with clause references, preserving all obligations, conditions, and binding verbs.
    input: A list of section dictionaries as returned by retrieve_policy.
    output: A plain-text summary document where each clause is summarised with its original clause number prefix (e.g. "2.3:"). Multi-condition clauses preserve all conditions. Binding verbs are kept verbatim. No external information is added.
    error_handling: If a clause cannot be summarised without meaning loss, quote the clause verbatim and flag with [VERBATIM]. If the input list is empty or malformed, output "ERROR: No valid sections to summarise."
