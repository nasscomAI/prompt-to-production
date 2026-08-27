skills:
  - name: process_input
    description: >
      Analyzes the input text and determines its category, priority,
      and explanation using rule-based keyword detection.
    input: >
      Text string provided through the command line argument (--text).
    output: >
      Structured result containing category, priority, reason, and flag fields.
    error_handling: >
      If the input text is empty or unclear, return category = "Other"
      and set flag = "NEEDS_REVIEW".

  - name: run_application
    description: >
      Executes the UC-0B application by reading user input, calling
      process_input, and printing the structured result.
    input: >
      Command line argument (--text) containing the user request.
    output: >
      Printed output displaying category, priority, reason, and flag.
    error_handling: >
      If required input is missing, display an error message and exit safely.
