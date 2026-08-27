skills:
  - name: retrieve_policy
    description: Loads a text file and builds a structured list of clause objects.
    input: Path string to a .txt file.
    output: Structured section data.

  - name: summarize_policy
    description: >
      Takes structured data and prompts an LLM using the constraints from
      agents.md to build a complete summary without dropping obligations
      or adding scope-bleed phrases.
