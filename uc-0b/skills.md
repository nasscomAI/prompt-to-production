# skills.md
name: retrieve_policy description: "Loads the HR leave policy .txt file and returns its complete content as structured numbered sections, preserving every clause, obligation, condition, deadline, limit, approver, exception, and consequence." input: "A path to the policy_hr_leave.txt file." output: "Structured numbered policy sections containing all source clauses, including clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2." error_handling:
"If the file path is invalid, the file does not exist, or the file cannot be read, return an explicit error and do not fabricate policy content."
"If any section is missing, unreadable, or ambiguous, flag the affected section instead of inferring its meaning."
"Preserve all conditions and multi-condition requirements, including all required approvers, deadlines, limits, and consequences."
name: summarize_policy description: "Takes structured policy sections and produces a compliant summary with clause references while preserving the exact meaning, obligations, conditions, deadlines, limits, approvers, exceptions, and consequences of the source policy." input: "Structured numbered policy sections returned by retrieve_policy." output: "A concise summary containing every required numbered clause with explicit clause references and no unsupported information." error_handling:
"If the input is missing, invalid, incomplete, or ambiguous, report the issue and do not invent or assume missing policy information."
"If any required clause is missing from the input, flag the missing clause rather than silently omitting it."
"If a clause cannot be summarized without changing its meaning, quote the clause verbatim and flag it."
"Preserve every condition in multi-condition obligations; never silently drop an approver, deadline, limit, exception, or consequence."
"Do not add information, interpretations, assumptions, or general HR practices that are not present in the source document."
"Prevent scope bleed by excluding unsupported phrases or claims such as 'as is standard practice', 'typically in government organisations', or 'employees are generally expected to'."