# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections with clause IDs preserved.
    input: File path string (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output: JSON object with numbered clauses as {clause_id: "2.3", text: "...", binding_verb: "must", obligation: "..."}
    error_handling: Fails with explicit error if file not found, unreadable, or lacks numbered sections. Does not guess clause structure.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clause conditions and binding verbs with clause references.
    input: JSON object of structured clauses from retrieve_policy
    output: Summary text with clause references (e.g., "[2.3]") and verbatim quotes for conditions that cannot be paraphrased
    error_handling: If any multi-condition clause risks meaning loss in paraphrase, quotes it verbatim and flags it for manual review. Never silently drops conditions or softens binding verbs.
