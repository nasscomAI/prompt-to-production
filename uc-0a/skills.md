# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: parse_complaint_text
    description: Parses raw complaint text to normalized tokens and key phrases for categorization.
    input: |
      string: raw complaint text (utf-8), e.g. "There is a big pothole on 5th and Main."
    output: |
      object
        - text: cleaned complaint text
        - tokens: array of tokens
        - key_phrases: array of extracted phrases
    error_handling: |
      If input is empty or not text, return error object {error: "invalid_input", message: "Complaint text must be nonempty string"}.

  - name: classify_complaint
    description: Classifies parsed complaint into category, priority, and provides explanation.
    input: |
      object with fields:
        - text: normalized complaint text
        - key_phrases: array of phrases
    output: |
      object
        - category: one of [Pothole, WaterLeak, PowerOutage, Noise, TrashCollection, StreetLight, Graffiti, TreeDamage, Other]
        - priority: one of [Low, Medium, High, Urgent]
        - reason: string with evidence from complaint text
        - flag: optional string (e.g. NEEDS_REVIEW)
    error_handling: |
      If classification is ambiguous, set category: Other, priority: Medium, flag: NEEDS_REVIEW, and reason: "Ambiguous complaint text".

