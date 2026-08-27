skills:
  - name: retrieve_policy
    description: Loads the 'policy_hr_leave.txt' file from '../data/policy-documents/' and returns the content as structured numbered sections.
    input: Path to the .txt policy document (string).
    output: Structured sections of the policy for analysis.
    error_handling: Raise an error if the file is missing or unreadable.

  - name: summarize_policy
    description: Produces a summary of the HR leave policy, preserving all 10 core clauses and their conditions.
    input: Structured policy sections.
    output: .txt summary file to be saved at 'uc-0b/summary_hr_leave.txt'.
    error_handling: If core clauses are missing from the input, return an 'INCOMPLETE' status and list missing sections.

