name: retrieve\_documents

description: Loads and indexes policy documents by section number

input:

&#x20; type: list

&#x20; format: list of file paths

output:

&#x20; type: object

&#x20; format: dictionary of documents with section mappings

error\_handling:

&#x20; If any file missing, return error



\---

name: answer\_question

description: Answers question using a single document source or returns refusal

input:

&#x20; type: string

&#x20; format: user question

output:

&#x20; type: string

&#x20; format: answer with citation OR refusal template

error\_handling:

&#x20; If no relevant section found, return refusal template exactly

&#x20; If multiple documents required, refuse instead of combining

