name: retrieve\_policy

description: Loads policy text file and structures it into numbered clauses

input:

&#x20; type: string

&#x20; format: file path to policy document

output:

&#x20; type: object

&#x20; format: structured clauses with clause numbers and text

error\_handling:

&#x20; If file not found, return error and stop execution

&#x20; If file is empty, return error



\---

name: summarize\_policy

description: Generates clause-preserving summary from structured policy

input:

&#x20; type: object

&#x20; format: structured clauses

output:

&#x20; type: text

&#x20; format: summary with clause references

error\_handling:

&#x20; If any clause is missing, fail the process

&#x20; If conditions are dropped, fail the process

