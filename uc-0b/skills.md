skills:

  - name: load_hr_policy
    description: Load the approved HR leave policy document and make its sections available for summarization.
    input:
      type: policy document
      format: Text file: policy_hr_leave.txt
    output:
      type: indexed policy
      format: Sections retrievable by section number.
    error_handling: If the source document cannot be loaded, report the error instead of inventing policy content.

  - name: summarize_leave_policy
    description: Produce a complete summary of the HR leave policy while preserving every required condition, restriction, limit, date, deadline, and approval requirement.
    input:
      type: indexed HR leave policy
      format: Policy sections from policy_hr_leave.txt
    output:
      type: policy summary
      format: Concise summary containing all ten required sections.
    error_handling: Reject or revise summaries that omit required clauses, weaken mandatory requirements, change numerical values, or invent information.

  - name: verify_policy_summary
    description: Verify that the generated summary faithfully represents all required HR leave policy clauses.
    input:
      type: policy summary
      format: Generated summary with section references.
    output:
      type: validation result
      format: PASS when all required clauses and conditions are preserved; otherwise FAIL with the missing or altered requirement.
    error_handling: Check every required section individually and reject summaries with clause omission, scope bleed, obligation softening, altered numbers, or incorrect approval chains.