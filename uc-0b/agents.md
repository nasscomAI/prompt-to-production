# UC-0B Agents

## Summary Generator
- Role: Reads policy documents and generates human-readable summaries.
- Input: CSV file with document IDs and text content.
- Output: CSV or TXT file containing summaries.
- Behavior: Must include **every numbered clause** from input.
- Constraints: Do not drop or modify clauses, preserve original meaning.

## Execution Flow
1. Read input CSV (`read_input()`).
2. Process each document: split into clauses, include all.
3. Generate summary text per document.
4. Save results to output file.
5. Print completion message.

## Notes
- This agent is CRAFT-tested: follows completeness, relevance, and clarity.