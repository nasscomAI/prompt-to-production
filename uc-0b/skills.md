skills:



\- name: retrieve\_policy

&#x20; description: Load a policy text file and return content as structured numbered sections.

&#x20; input: policy\_file (.txt)

&#x20; output: structured\_sections

&#x20; error\_handling: Return an error if the file cannot be found or read.



\- name: summarize\_policy

&#x20; description: Create a compliant summary while preserving obligations, approvals, restrictions, and clause references.

&#x20; input: structured\_sections

&#x20; output: compliant\_summary

&#x20; error\_handling: Flag clauses that cannot be summarized without meaning loss.

