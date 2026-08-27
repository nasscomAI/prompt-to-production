# UC-0B Skills

## Skill: retrieve_policy
**Input:** Path to .txt policy file
**Output:** Structured dict of sections -> numbered clauses with their text
**Logic:**
- Read file line by line
- Identify section headers (ALL CAPS lines or === lines)
- Group numbered clauses (e.g. 2.3, 5.2) under their section
- Return structure preserving all clause numbers and text

## Skill: summarize_policy
**Input:** Structured clause dict from retrieve_policy
**Output:** Written summary with clause references
**Logic:**
- Iterate every clause in order
- Apply binding verb preservation rule
- Apply multi-condition preservation rule
- Flag any clause where summary would lose meaning
- Never add information not in source
