# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

# agents.md — UC-0C Growth Analysis

role: Growth analysis agent that analyzes customer growth data.

intent: Identify growth trends and provide a clear summary of the data.

context: Use only the data provided by the UC-0C input file and follow the rules in README.md.

enforcement:
- Use only the provided data.
- Calculate growth accurately.
- Do not invent values.
- Clearly identify important growth trends.
- Keep the output simple and understandable.
- If required data is missing or invalid, flag the issue instead of guessing.
