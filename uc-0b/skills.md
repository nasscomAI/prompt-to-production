# skills.md — UC-0B HR Leave Policy Advisor

skills:
  - name: categorise_leave
    description: Classify a free-text leave query into one of the six recognised leave categories.
    input: "A string containing the employee's leave question or request (free text)."
    output: >
      A dict with keys:
        leave_type (str): One of Annual Leave | Sick Leave | Maternity Leave | Paternity Leave | Leave Without Pay | Compensatory Off
        confidence (str): HIGH | MEDIUM | LOW
        flag (str): NEEDS_REVIEW if confidence is LOW, else blank
    error_handling: >
      If the query does not match any leave category, return leave_type: UNKNOWN
      and flag: NEEDS_REVIEW. Never guess a category — ambiguity must be surfaced.

  - name: check_eligibility
    description: Given a categorised leave type and employee context, determine eligibility and list all conditions.
    input: >
      A dict with keys:
        leave_type (str): The categorised leave type from categorise_leave
        employee_type (str): permanent | contractual
        duration_days (int): Number of leave days requested
        advance_notice_days (int): How many days in advance the request is made
        adjacent_to_holiday (bool): Whether the leave is adjacent to a public holiday
        remaining_balance (dict): Keys are leave types, values are remaining days
        additional_context (str): Any extra info (e.g., "third child", "medical certificate available")
    output: >
      A dict with keys:
        verdict (str): ELIGIBLE | NOT_ELIGIBLE | CONDITIONAL
        conditions (list[str]): List of conditions that must be met
        required_documents (list[str]): Forms or certificates needed
        required_approvals (list[str]): Who must approve
        policy_references (list[str]): Clause numbers cited (e.g., §2.3, §3.2)
        explanation (str): Plain-language summary of the decision
        warnings (list[str]): Any edge-case warnings (e.g., carry-forward expiry)
    error_handling: >
      If employee_type is not permanent or contractual, return verdict: NOT_ELIGIBLE
      with explanation citing §1.2. If leave_type is UNKNOWN, return verdict: NOT_ELIGIBLE
      with explanation directing to HR.

  - name: calculate_leave_balance
    description: Calculate accrued, used, and remaining leave balances for an employee.
    input: >
      A dict with keys:
        employee_type (str): permanent | contractual
        months_of_service (int): Total months since joining
        annual_leave_used (int): Annual leave days already taken this year
        sick_leave_used (int): Sick leave days already taken this year
        carry_forward_days (int): Days carried forward from previous year (max 5)
    output: >
      A dict with keys:
        annual_leave_accrued (float): 1.5 × months_of_service (capped at 18/year)
        annual_leave_remaining (float): accrued - used + carry_forward
        sick_leave_remaining (int): 12 - sick_leave_used
        carry_forward_eligible (int): min(annual_leave_remaining, 5)
        summary (str): Plain-language balance summary
    error_handling: >
      If months_of_service is negative or leave_used exceeds entitlement,
      return an error message and flag for HR review.

  - name: process_leave_query
    description: End-to-end pipeline — takes a free-text query, categorises it, checks eligibility, and returns a complete advisory response.
    input: "A string containing the employee's leave question (free text) plus optional employee context dict."
    output: >
      A dict combining outputs of categorise_leave and check_eligibility,
      plus a human-readable advisory_response string suitable for display.
    error_handling: >
      If any sub-skill fails, return partial results with clear indication
      of which step failed and why. Never return an empty response.
