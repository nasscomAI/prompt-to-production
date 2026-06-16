---
name: summarize-policy
description: Takes structured policy sections, produces compliant summary with every clause preserved and all conditions intact
---

## What I do
- Take structured policy sections from retrieve_policy
- Produce a summary that preserves every numbered clause
- Ensure all multi-condition obligations keep every condition
- Flag clauses that cannot be summarised without meaning loss

## Input
- Structured sections: object with clause numbers and text

## Output
- Summary string with all clauses and conditions preserved

## Error handling
- If a clause cannot be summarised, quote it verbatim and add a flag
