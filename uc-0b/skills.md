# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads the policy text file and returns its numbered sections for faithful summarization.
    input: A UTF-8 text file path containing the policy document.
    output: Structured policy sections containing clause numbers and source text.
    error_handling: If the file cannot be read or a section cannot be identified reliably, stop and report the problem rather than inventing missing content.

  - name: summarize_policy
    description: Produces a clause-referenced summary while preserving every obligation and condition from the source.
    input: Structured policy sections containing clause numbers and source text.
    output: A UTF-8 text summary containing every required clause reference, its obligation, and all material conditions.
    error_handling: If a clause cannot be summarized without meaning loss, preserve its source wording and mark it for review rather than guessing or omitting it.