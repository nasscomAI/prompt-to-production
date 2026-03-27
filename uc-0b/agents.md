# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  [FILL IN: Who is this agent? What is its operational boundary?]

intent: >
  [FILL IN: What does a correct output look like — make it verifiable]

context: >
  [FILL IN: What information is the agent allowed to use? State exclusions explicitly.]

enforcement:
  - "[FILL IN: Specific testable rule 1]"
  - "[FILL IN: Specific testable rule 2]"
  - "[FILL IN: Specific testable rule 3]"
  - "[FILL IN: Refusal condition — when should the system refuse rather than guess?]"

  1. Every clause must be included
2. Multi-condition clauses must preserve ALL conditions
3. No assumptions or added information allowed
4. Use verbatim quoting if meaning may change
