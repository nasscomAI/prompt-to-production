skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its content into structured, numbered sections for precise analysis.
    input: String representing the absolute path to the policy .txt file.
    output: A list of objects containing clause identifiers (e.g., "2.3") and their raw text content.
    error_handling: If the file is inaccessible, empty, or lacks numbered clauses, it returns an error notification and halts the summarization pipeline.

  - name: summarize_policy
    description: Produces a compliant summary of structured policy sections while strictly enforcing clause preservation and condition accuracy.
    input: A list of structured objects representing numbered policy clauses and their text.
    output: A formatted text summary where each entry preserves the core obligation, binding verbs, and all associated conditions.
    error_handling: If a clause risks meaning loss, obligation softening, or scope bleed, the skill quotes the clause verbatim and applies a "REQUIRES_REVIEW" flag.
