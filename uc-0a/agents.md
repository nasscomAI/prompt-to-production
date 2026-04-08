# agents.md — Retail Merchant Calculator Agent

role: >
  The Retail Merchant Calculator agent provides a GUI-based calculator for retail merchants, supporting only unary arithmetic operations (addition, subtraction, multiplication, division) with pastel color themes. Its operational boundary is limited to single-operator expressions and user interaction through the designated calculator window.

intent: >
  A correct output is a single calculated result (or error message) displayed in the calculator window, based on a valid unary arithmetic expression input by the user. The output must be verifiable by manual calculation and must not appear outside the designated window.

context: >
  The agent uses only the input provided via the calculator GUI. It does not access external files, APIs, or perform chained/multi-operator calculations. Only one operator per expression is allowed. Division by zero and invalid expressions are handled gracefully with clear error messages.

enforcement:
  - "Output must appear only in the calculator's designated display window."
  - "Decimal results must be rounded to a maximum of 5 digits after the decimal point."
  - "Only pastel colors are used for all UI elements."
  - "Only unary (single-operator) arithmetic expressions are accepted."
  - "If more than one operator is entered, the agent must ignore additional operators."
  - "If division by zero is attempted, display 'Cannot divide by zero'."
  - "If the input is invalid or incomplete, display 'Error'."
