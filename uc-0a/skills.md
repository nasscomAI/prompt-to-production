# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: Prompt_Analyzer
    description: Analyzes user prompts to understand intent, context, and required actions.
    input: Raw user prompt as a string (natural language text).
    output: Structured data including intent, keywords, and task type (JSON format).
    error_handling: Returns a clear error message if the prompt is empty, unclear, or lacks sufficient context.

  - name: Response_Generator
    description: Generates meaningful and context-aware responses based on analyzed input.
    input: Structured data (intent, keywords, context) in JSON format.
    output: Human-readable response text tailored to the user query.
    error_handling: Provides a fallback response asking for clarification if input data is incomplete or invalid.

  - name: Validation_Checker
    description: Validates input and output data to ensure correctness and completeness.
    input: User input or generated output in string/JSON format.
    output: Boolean result (valid/invalid) along with validation messages.
    error_handling: Flags errors with specific messages indicating missing or incorrect fields.

  - name: Context_Manager
    description: Maintains and manages conversation context for better continuity.
    input: Previous conversation history and current user input (JSON format).
    output: Updated context including relevant past interactions.
    error_handling: Resets or trims context if data is corrupted or exceeds limits.

  - name: Output_Formatter
    description: Formats responses into clean, structured, and readable outputs.
    input: Raw generated response text.
    output: Well-structured formatted response (Markdown or plain text).
    error_handling: Applies default formatting if input is inconsistent or malformed.
