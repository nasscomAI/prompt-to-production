# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of numbered sections, preserving clause numbers and original wording.
    input: file_path (string path to a .txt policy document).
    output: A dict with keys 'title' (string) and 'sections' (list of dicts, each with 'number' and 'text').
    error_handling: If the file does not exist or cannot be read, raise FileNotFoundError with the path. If the file is empty, raise ValueError indicating the document has no content to summarise.

  - name: summarize_policy
    description: Takes the full policy text and produces a clause-complete summary with clause references, preserving all conditions and binding obligations from the source.
    input: policy_text (string, full content of the policy document).
    output: A string containing the summary, with each clause referenced by its original number (e.g. [2.4]) and no additions or omissions.
    error_handling: If the Claude API call fails, raise RuntimeError. Never return a partial summary — either the full clause-complete summary is returned or an error is raised, so the caller always knows whether the output is complete.
