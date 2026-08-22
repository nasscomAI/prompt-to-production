skills:
  - name: retrieve_policy
    description: Loads a raw text policy document from disk and verifies its structure.
    input: String path to the target text file.
    output: String containing the raw text payload.
    error_handling: System catches FileNotFoundError and halts execution with a clean error message.

  - name: summarize_policy
    description: Generates a high-fidelity summary ensuring that multi-condition clauses preserve all original constraints.
    input: Raw text content from the policy document.
    output: Structured summary text file with mandatory clause-level preservation.
    error_handling: Enforces hardcoded verification metrics to ensure mandatory sections are present.
