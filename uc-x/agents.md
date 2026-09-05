# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.
# agents.md — UC-X

role: General problem-solving agent for the UC-X task.

intent: Analyze the provided input, identify the required task, and produce the correct output.

context: Use only the information and rules provided in README.md and the input data.

enforcement:
- Follow the requirements defined in README.md.
- Use only the provided input data.
- Do not invent information.
- Produce output in the required format.
- If required information is missing or invalid, clearly flag the issue.
- Keep the final result clear and understandable.
