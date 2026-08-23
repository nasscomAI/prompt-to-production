skills:

  - name: retrieve_policy
    description: Loads the policy text file and returns its content as structured numbered sections.
    input: A policy .txt file containing the source policy document.
    output: Structured numbered policy sections containing the original policy content.
    error_handling: If the file is missing, unreadable, or contains an unclear clause structure, report the problem and do not invent or infer missing policy content.

  - name: summarize_policy
    description: Produces a concise policy summary that preserves every required clause, obligation, condition, exception, threshold, deadline, and approval requirement.
    input: Structured numbered policy sections returned by retrieve_policy.
    output: A clause-referenced policy summary containing all required obligations and conditions from the source document.
    error_handling: If a clause cannot be summarized without losing or changing its meaning, preserve the clause verbatim and flag it for review rather than guessing or omitting information.