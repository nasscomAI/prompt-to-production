# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [retrieve_policy]
    description: [Load the supplied policy .txt file and return its contents as structured
      numbered sections while preserving clause numbers and source wording]
    input: [ A policy text file..]
    output: [ Structured policy sections containing section numbers, clause numbers,
      and clause text.]
    error_handling: [If the policy cannot be read or a clause cannot be parsed reliably,
      preserve the original text and flag the affected clause for review.]

  - name: [summarize_policy]
    description: [Produce a compliant policy summary from the structured numbered sections
      while preserving every clause, condition, exception, threshold, deadline,
      approval requirement, consequence, and prohibition.]
    input: [Structured numbered policy sections returned by retrieve_policy.]
    output: [ A clause-referenced summary containing every numbered clause from the
      source policy.]
    error_handling: [Never invent missing information. If a clause cannot be summarized
      without meaning loss, quote it verbatim and flag it for review.]
