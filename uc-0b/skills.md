# Policy Summarizer Skills

## retrieve_policy
- **Input:** Path to the `.txt` policy file.
- **Task:** 
  1. Load the text file.
  2. Parse the content into a structured format (e.g., sections, numbered clauses).
  3. Identify and extract all numbered clauses.
- **Output:** A structured collection of policy clauses.

## summarize_policy
- **Input:** Structured collection of policy clauses.
- **Task:** 
  1. For each of the 10 target clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2), extract the core obligation and binding verb.
  2. Synthesize a summary for each clause, ensuring all conditions (e.g., dual-approver requirements) are preserved.
  3. Ensure no external information or "scope bleed" is added.
  4. Format the final output as a numbered list with clause references.
- **Output:** A text summary of the policy's critical obligations.
