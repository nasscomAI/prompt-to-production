skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a structured string of numbered sections.
    input: file_path (str) — absolute or relative path to the policy .txt file.
    output: str — full file content, preserving all section headings and clause numbers.
    error_handling: Raises FileNotFoundError with the path if the file does not exist. Raises ValueError if the file is empty.

  - name: summarize_policy
    description: Takes the full text of a policy document and produces a clause-accurate summary preserving all clause numbers, multi-conditions, and binding verbs.
    input: content (str) — full policy text as returned by retrieve_policy; client (OpenAI) — initialised API client.
    output: str — structured summary with the same section groupings as the source, every clause number present, all conditions intact, no additions.
    error_handling: If the API call fails, raises the underlying OpenAI exception. Does not retry silently or fall back to a truncated response.
