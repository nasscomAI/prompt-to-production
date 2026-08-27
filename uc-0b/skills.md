# skills.md — UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Extracts and structures policy content from a text file into a mapping of clause numbers to their exact text.
    input: File path to a policy document (.txt).
    output: A dictionary where keys are clause numbers (e.g., "2.3", "5.2") and values are the verbatim clause strings.
    error_handling: >
      Identifies and logs unnumbered or malformed sections. If the input file is not found, 
      it halts and reports a missing source error.

  - name: summarize_policy
    description: Condenses structured policy clauses into a precise summary while strictly preserving all obligations and conditions.
    input: A structured dictionary of policy clauses (from retrieve_policy).
    output: >
      A summary document where every source clause is accounted for, using original binding verbs 
      and preserving all multi-party approval requirements.
    error_handling: >
      If a clause is identified as high-risk for meaning loss (e.g., complex multi-approver chains), 
      the skill refuses to summarize and instead provides a verbatim quote flagged as 'UNSUMMARIZABLE_OBLIGATION'.
