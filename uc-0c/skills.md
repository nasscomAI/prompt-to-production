# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: number_processing
    description: Processes numeric input and performs basic validation or formatting.
    input: Numeric value (int or float)
    output: Validated or formatted numeric result
    error_handling: If input is not a number → return "Invalid input"

  - name: calculation
    description: Performs basic arithmetic operations like addition, subtraction, multiplication, or division.
    input: Two numbers and an operation (+, -, *, /)
    output: Result of the calculation as a number
    error_handling: If invalid operation or division by zero → return "Calculation error"
