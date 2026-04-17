skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts content into structured numbered sections for precise cross-referencing.
    input: File path to the policy text document.
    output: A collection of sections keyed by clause number (e.g., '2.3', '5.2') with their raw text.
    error_handling: Refuses if the file is not found or if the structure lacks identifiable numbering.

  - name: summarize_policy
    description: Generates a high-integrity summary of clauses, ensuring all binding conditions and approvers are preserved.
    input: Structured policy sections and a list of mandatory clause numbers to include.
    output: A bulleted summary where each item is mapped to a clause number and preserves all mandatory conditions.
    error_handling: Flags a 'WARNING: Clause Missing' if any mandatory clause from the inventory is not found in the source.
