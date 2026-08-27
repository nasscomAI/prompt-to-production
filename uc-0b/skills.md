skills:
  - name: retrieve_policy
    description: Load a policy text file and parse it into numbered clauses for controlled summarization.
    input: "Policy file path (.txt)."
    output: "Structured list of sections: {section_number, clause_text, binding_verb}."
    error_handling: "If file is unreadable or required section numbers are missing, fail with an explicit retrieval/coverage error."

  - name: summarize_policy
    description: Generate a compliant summary that preserves obligations, conditions, and clause references.
    input: "Structured clauses from retrieve_policy."
    output: "Summary text with each covered point mapped to its source clause number."
    error_handling: "If paraphrasing would drop a condition or weaken obligation, insert a verbatim quote for that clause and flag it for manual review."
