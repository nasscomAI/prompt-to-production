skills:
  - name: retrieve_context
    description: Loads policy files (HR, IT, Finance) and parses them into sectional dictionaries to ensure precise citation and zero document blending.
    input: File paths to the 3 documents.
    output: A dictionary indexed by [policy_name][section_number].

  - name: generate_answer
    description: Executes the single-source reasoning logic. Returns an answer + citation OR the refusal template.
    input: Query text and policy index.
    output: String response.
    error_handling: Detects cross-document keywords (e.g., 'phone' + 'work files') and applies the IT Section 3.1 restrictive override.
