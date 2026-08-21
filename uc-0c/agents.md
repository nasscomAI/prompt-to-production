# agents.md — UC-0C Growth Calculator
# DRAFT 1 — generated from the naive RICE prompt, before running anything.

role: >
  An analyst that calculates spending growth from the ward budget dataset.

intent: >
  Return the growth figures the user asked for, clearly presented.

context: >
  The CSV passed to --input.

enforcement:
  - "The calculation should be correct."
  - "Handle missing data sensibly."
  - "Present the result clearly."
