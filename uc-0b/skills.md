# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections
    input: txt_path — path to policy file (e.g., policy_hr_leave.txt)
    output: dict mapping clause numbers (e.g., "2.3", "5.2") to full clause text as string
    error_handling: If file not found, raise FileNotFoundError with path included. If no numbered clauses found, return empty dict.
    error_handling_ambiguous: Reports lines that could not be parsed as clauses but does not fail; includes them as unstructured text if possible.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references
    input: clauses — dict mapping clause numbers to text (as returned by retrieve_policy); binding_verb_filter — optional list of clause numbers to filter by verb type
    output: string containing compliant summary with all numbered clauses present, preserving all conditions and binding verbs, with clause references
    error_handling: If clauses dict is empty, raises ValueError "No clauses found to summarize". If required clause is missing from input, includes placeholder noting omission.
    error_handling_ambiguous: Preserves all conditions in multi-condition obligations (e.g., clause 5.2 with both Department Head AND HR Director). Never drops conditions silently. Raises error if clause text cannot be parsed as expected.
