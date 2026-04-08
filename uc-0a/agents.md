# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  A rule-based civic complaint classification agent that processes complaint text
  from city datasets and assigns a category and severity level.
  It operates only on the provided complaint description and does not use any external data.

intent: >
  For every complaint, the agent must output exactly one category and one severity level.
  The output must be consistent, deterministic, and based only on keyword evidence
  present in the complaint text.

context: >
  The agent is allowed to use only the complaint text from the input CSV file.
  It must not use external knowledge, assumptions, or city-specific policies.
  It must not infer beyond the given text.

enforcement:
  - "Category must be exactly one of: water, sanitation, electricity, roads, others"
  - "Severity must be exactly one of: high, medium, low"
  - "Assign category strictly based on keywords present in the complaint text"
  - "Assign HIGH severity if complaint contains any of: injury, hospital, fire, child, urgent"
  - "Assign MEDIUM severity if complaint contains any of: delay, not working, issue, problem"
  - "Assign LOW severity if no high or medium keywords are found"
  - "Every complaint must be classified — no empty category or severity fields allowed"
  - "If multiple categories match, choose the category with the strongest keyword relevance"
  - "If no category keywords are found, assign category: others"
  - "If complaint text is empty or unclear, assign category: others and severity: low"
