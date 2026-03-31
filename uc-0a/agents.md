# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  [FILL IN: Who is this agent? What is its operational boundary?]

intent: >
  [FILL IN: What does a correct output look like — make it verifiable]

context: >
  [FILL IN: What information is the agent allowed to use? State exclusions explicitly.]

enforcement:
  - "[FILL IN: Specific testable rule 1 — e.g. Category must be exactly one of: Pothole, Flooding, ...]"
  - "[FILL IN: Specific testable rule 2 — e.g. Priority must be Urgent if description contains: injury, child, school, ...]"
  - "[FILL IN: Specific testable rule 3 — e.g. Every output row must include a reason field citing specific words from the description]"
  - "[FILL IN: Refusal condition — e.g. If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW]"
