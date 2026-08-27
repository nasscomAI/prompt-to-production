# skills.md

skills:

- name: retrieve_policy
  description: Loads a .txt policy file and returns content structured by numbered clauses as JSON.
  input: File path (string) pointing to a .txt policy document containing numbered HR clauses.
  output: JSON object with clauses as key-value pairs. Format { "2.3": "14-day advance notice required", "2.4": "Written approval required...", etc. } All clauses must be extracted verbatim.
  error_handling: If file not found, raise FileNotFoundError with path. If file contains non-numbered text, flag as warning and return only numbered sections. Refuse to proceed if fewer than 10 numbered clauses detected (incomplete document).

- name: summarize_policy
  description: Takes structured policy clauses and produces a compliant summary preserving all clauses and conditions with zero omission or scope bleed.
  input: JSON object of numbered clauses from retrieve_policy. Each key is clause ID (e.g., "2.3"), value is clause text verbatim.
  output: Text summary with header "POLICY SUMMARY" listing all clauses with their binding verbs and complete conditions. Format: "Clause 2.3 [must]: 14-day advance notice required. Clause 2.4 [must]: Written approval required before leave commences. Verbal not valid." Multi-condition clauses must list ALL conditions (AND preserved, never dropped). If any clause risks meaning loss through summarization, output as "HIGH FIDELITY: DIRECT QUOTE: [full text]".
  error_handling: If input lacks expected clause IDs, return error "Missing clauses—cannot summarize incomplete policy." If asked to add domain assumptions or generalize, refuse with "Cannot summarize without risking condition loss." If any bound condition cannot be preserved in summary form, flag clause with HIGH FIDELITY marker instead of paraphrasing.
