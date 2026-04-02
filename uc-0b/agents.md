# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: > policy_agent

intent: >
  Generate a lossless summary of the HR leave policy ensuring no clause omission, no condition drop, and no obligation softening


context: >
  clause_2_3: "Employee must provide 14-day advance notice before taking leave"
  clause_2_4: "Leave must have written approval before commencement; verbal approval is not valid"
  clause_2_5: "Unapproved absence will be treated as Loss of Pay regardless of any later approval"
  clause_2_6: "A maximum of 5 leave days may be carried forward; any excess above 5 are forfeited on 31 December"
  clause_2_7: "Carried-forward leave must be used between January and March or will be forfeited"
  clause_3_2: "Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours"
  clause_3_4: "Sick leave taken before or after a holiday requires a medical certificate regardless of duration"
  clause_5_2: "Leave Without Pay requires approval from both the Department Head and the HR Director"
  clause_5_3: "Leave Without Pay exceeding 30 days requires approval from the Municipal Commissioner"
  clause_7_2: "Leave encashment during service is not permitted under any circumstances"


enforcement:
  - Every listed clause must be present in the summary output
  - No clause may be omitted or merged in a way that changes meaning
  - All conditions within a clause must be fully preserved
  - Dual approvals in clause 5.2 must explicitly include both Department Head and HR Director
  - Binding verbs (must, requires, will, not permitted) must not be weakened or altered
  - No additional assumptions, interpretations, or external phrasing allowed
  - If any clause cannot be summarized without meaning loss, include it verbatim and flag it