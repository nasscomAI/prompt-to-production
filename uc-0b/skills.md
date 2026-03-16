# skills.md

skills:
  - name: nuanced_summarization
    description: Distills complex transcripts into a concise 2-sentence summary while preserving all technical facts and user intent.
    input: Raw text string (customer support transcript).
    output: String (2-sentence summary).
    error_handling: If the input is empty or nonsensical, returns "error: insufficient_context".

  - name: sentiment_preservation
    description: Analyzes the emotional tone of the transcript to ensure the summary reflects the user's actual experience without dilution.
    input: Raw text string.
    output: String (One of: Positive, Neutral, Negative).
    error_handling: If tone is ambiguous, defaults to "Neutral" and flags for manual review.

  - name: keyword_guardian
    description: Extracts and protects specific technical entities like error codes, product names, or monetary amounts from being generalized.
    input: Raw text string.
    output: List of strings (key technical entities).
    error_handling: Returns an empty list if no technical entities are detected.