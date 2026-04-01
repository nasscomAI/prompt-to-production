\# skills.md — UC-0B Summary That Changes Meaning



skills:

&#x20; - name: retrieve\_policy

&#x20;   description: Loads the HR policy text file and returns its content as structured sections with numbered clauses.

&#x20;   input: file\_path (string) - path to the policy .txt file

&#x20;   output: A dictionary with section headers as keys and list of clause strings as values

&#x20;   error\_handling: If file not found, raise clear error. If file empty, return empty structure.



&#x20; - name: summarize\_policy

&#x20;   description: Takes structured policy sections and produces a compliant summary that preserves every numbered clause with all conditions intact.

&#x20;   input: structured\_policy (dict) - policy sections with clauses

&#x20;   output: A string containing the complete summary with section headers and all clauses

&#x20;   error\_handling: If any critical clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing from output, raise error. If clause too complex to summarize, quote verbatim and flag.



&#x20; - name: validate\_summary

&#x20;   description: Checks that the generated summary contains all numbered clauses from the source with complete conditions preserved.

&#x20;   input: source\_text (string), summary\_text (string)

&#x20;   output: Boolean (True if valid, False if clauses missing or conditions dropped)

&#x20;   error\_handling: Returns detailed list of missing clauses or softened conditions for debugging.

