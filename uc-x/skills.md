

skills:
  - name: execute_ucx_task
    description: Executes the specific UC-X workflow using only the provided instructions, approved inputs, and required output schema.
    input: The UC-X task definition as structured or plain text input, including source records, business rules, allowed values, and the expected output format.
    output: A structured or plain text task result that follows the required UC-X schema, field rules, and decision logic exactly.
    error_handling: If required inputs are missing, conflicting, or too ambiguous to complete the task safely, do not guess; instead return a safe failure, review flag, or clarification response as required by the UC-X workflow.

  - name: validate_ucx_output
    description: Verifies that the generated UC-X result is fully compliant with the provided schema, constraints, and evidence boundaries before final output.
    input: The original UC-X task definition, provided inputs, and the generated output as structured or plain text data.
    output: A validated UC-X result that matches required fields, allowed values, formatting rules, and evidence-based decision constraints.
    error_handling: If the output contains unsupported inferences, schema violations, invalid labels, missing required fields, or rule mismatches, correct them when possible; otherwise reject the result and return a safe review or clarification state.