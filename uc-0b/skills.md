skills:
  - name: retrieve_policy
    description: >
      Loads a .txt HR policy document and parses it into structured numbered clauses.
    input: File path to policy document (string)
    output: >
      Dictionary where keys are clause numbers (e.g., "2.3", "5.2") and values are clause text.
    processing_steps:
      - Read text file
      - Identify numbered sections using regex (e.g., 2.3, 5.2)
      - Extract full clause text for each section
      - Normalize whitespace and formatting
    error_handling:
      - If file not found:
          raise error "Input file not found"
      - If no clauses detected:
          return empty dictionary and flag NEEDS_REVIEW
      - If clause numbering is inconsistent:
          attempt partial extraction and flag NEEDS_REVIEW

  - name: summarize_policy
    description: >
      Produces a clause-by-clause summary that preserves all obligations,
      conditions, and legal meaning without omission or softening.
    input: >
      Structured dictionary of clauses from retrieve_policy
    output: >
      Text summary with clause numbers, preserving all 10 required clauses
    processing_steps:
      - Iterate through required clause list (ground truth)
      - Match each clause with extracted content
      - Summarize each clause individually
      - Preserve:
          - All conditions
          - All actors (e.g., Department Head AND HR Director)
          - Binding verbs (must, requires, not permitted)
      - If clause contains multiple conditions → ensure all are included
      - If summarization risks meaning loss → quote clause verbatim
      - Compile final structured summary

    error_handling:
      - If a required clause is missing:
          include placeholder:
            "Clause X.X not found in document"
          flag NEEDS_REVIEW
      - If multiple conditions cannot be safely summarized:
          quote original clause verbatim
          flag NEEDS_REVIEW
      - If ambiguity in interpretation:
          avoid guessing
          use original wording
          flag NEEDS_REVIEW
      - If extra (non-required) clauses appear:
          ignore unless explicitly needed

    validation:
      - Ensure all 10 clauses are present in output
      - Ensure no condition is dropped
      - Ensure no verb softening
      - Ensure no added external knowledge
