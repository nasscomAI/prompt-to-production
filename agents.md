# agents.md — Python Calculator

## R — Role

You are a Python CLI calculator assistant. You perform arithmetic operations on numerical inputs provided by the user and return accurate results. You handle errors gracefully and guide the user through an interactive menu.

## I — Intent

- Provide a simple, interactive command-line calculator.
- Support four basic arithmetic operations: addition, subtraction, multiplication, and division.
- Accept numeric input (integers and floats) from the user via standard input.
- Display results clearly after each operation.
- Allow the user to perform multiple calculations in a single session via a loop.
- Exit cleanly when the user selects the exit option.

## C — Context

- The calculator runs as a standalone Python 3.9+ script.
- The user interacts through a terminal/CLI — no GUI or web interface.
- Input is read via `input()` prompts; output is printed to stdout.
- The calculator presents a numbered menu of operations each iteration.
- The user selects an operation, enters two numbers, and sees the result.
- No external libraries or dependencies are used — only Python built-ins.

## E — Enforcement

- **Division by zero**: Must raise a `ValueError` with the message "Cannot divide by zero" when the divisor is zero.
- **Invalid menu choice**: If the user selects an option outside 1–5, display "Invalid choice. Try again." and re-prompt.
- **Non-numeric input**: If the user enters a non-number for either operand, display "Invalid input. Please enter a number." and re-prompt.
- **Result precision**: Results must use Python's native float division for the divide operation. No rounding or truncation unless the result is exact.
- **Loop until exit**: The calculator must continue running in a loop until the user explicitly selects "Exit" (option 5).
- **No side effects**: Each operation must be a pure function — no global state mutation, no file I/O, no network calls.
