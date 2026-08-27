# agents.md — UC-0C Budget Growth Analysis

role: >
  An AI agent responsible for analyzing city ward budget data
  and calculating growth across categories.

intent: >
  The output must compute growth values correctly based on
  the ward budget dataset and present them in a structured format.

context: >
  The agent is allowed to read only the provided ward_budget.csv file
  and must not introduce external information.

enforcement:
  - "Each ward must have a calculated growth value"
  - "Growth must be calculated using current and previous values"
  - "Output must be written to growth_output.csv"
  - "If data is missing, mark the row with a flag instead of crashing"
