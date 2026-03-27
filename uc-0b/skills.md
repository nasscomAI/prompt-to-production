# skills.md — UC-0B Policy Summarization

skills:
  - name: retrieve_policy
    description: Loads a raw .txt policy file and returns the content organized into structured, numbered sections for precise analysis.
    input: Absolute path to the .txt policy file.
    output: A collection of structured strings representing each numbered clause and section.
    error_handling: Return a clear error if the file cannot be found or if the structure is too malformed to parse.

  - name: summarize_policy
    description: Processes structured policy sections into a condensed summary while strictly adhering to R.I.C.E. reinforcement rules for clause retention and condition preservation.
    input: Structured policy sections and clause map.
    output: A precision-crafted summary with clause references and preserved obligations.
    error_handling: If a section is missing from the input, explicitly note it in the output instead of skipping or guessing its content.
