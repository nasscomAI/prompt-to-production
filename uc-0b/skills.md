# skills.md

skills:
  - name: retrieve_policy
    description: Load the policy text file and parse its contents into a dictionary of numbered clauses.
    input: file_path (string) - Path to the leave policy text file.
    output: dict - Mapping of clause numbers (e.g., '2.3') to their full textual descriptions.
    error_handling: Raise FileNotFoundError if the input file does not exist. If the file is empty, return an empty dictionary.

  - name: summarize_policy
    description: Formulate a compliant summary from the retrieved clauses by quoting them verbatim and flagging them to preserve exact obligations and conditions.
    input: clauses (dict) - Mapping of clause numbers to their text.
    output: string - A structured document containing all clauses formatted with references, verbatim texts, and flags.
    error_handling: Return an empty string if the input dict is empty.

examples:
  - input:
      "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."
      "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    expected_output: |
      CMC EMPLOYEE LEAVE POLICY SUMMARY
      =================================
      
      [Clause 2.3] (VERBATIM):
      Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.
      
      [Clause 5.2] (VERBATIM):
      LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.

test_guidance:
  - Ensure all 10 ground truth clauses from the policy document are correctly retrieved.
  - Verify that the summary matches the original clause text exactly, maintaining all multi-condition approvals.

