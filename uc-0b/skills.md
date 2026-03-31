skills:
  - name: retrieve_policy
    description: Loads a .txt HR policy file and returns its content logically organized as structured, numbered sections.
    input: A string representing the file path to the policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A list or dictionary of structured sections with their respective clause numbers and verbatim text.
    error_handling: Return a clear error if the file cannot be found, is corrupted, or if text cannot be properly parsed. Do not attempt to guess or hallucinate text.

  - name: summarize_policy
    description: Processes structured policy sections to generate a highly compliant summary that rigorously preserves all obligations, multi-conditions, and clauses with zero scope bleed.
    input: The structured clauses and multi-condition obligations outputted by `retrieve_policy`.
    output: A complete text summary containing precise clause references, maintaining the exact intent and conditions, suitable for saving to `uc-0b/summary_hr_leave.txt`.
    error_handling: If a clause cannot be summarized without losing meaning or softening the obligation, quote the clause verbatim and flag it. Refuse to execute if the input sections are empty.
