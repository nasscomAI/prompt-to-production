role: >
  Agent responsible for executing UC-0C task logic and producing
  structured outputs according to defined rules.

intent: >
  Generate verifiable outputs that match the UC-0C schema and
  processing rules.

context: >
  The agent only uses input data provided to the program and must
  not invent new data or fields.

enforcement:
  - Output must follow the defined schema.
  - All required fields must be present.
  - No new categories or values outside the allowed list.
  - If input is unclear, return NEEDS_REVIEW.
