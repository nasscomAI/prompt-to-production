skills:



&#x20; - name: retrieve\_documents



&#x20;   description: >

&#x20;     Load all three approved policy documents and index their

&#x20;     numbered sections by document name and section number.



&#x20;   input:

&#x20;     type: directory

&#x20;     value: ../data/policy-documents/



&#x20;   output:

&#x20;     type: structured\_documents

&#x20;     fields:

&#x20;       - document\_name

&#x20;       - section\_number

&#x20;       - section\_text



&#x20;   error\_handling:

&#x20;     - Fail clearly if a required policy document is missing.

&#x20;     - Do not substitute external documents.

&#x20;     - Do not modify source policy text.



&#x20; - name: answer\_question



&#x20;   description: >

&#x20;     Search the indexed policy documents and return an answer only

&#x20;     when the answer can be supported by one document and one or

&#x20;     more sections without blending documents.



&#x20;   input:

&#x20;     type: question

&#x20;     value: employee\_policy\_question



&#x20;   output:

&#x20;     type: answer

&#x20;     fields:

&#x20;       - answer

&#x20;       - source\_document

&#x20;       - section\_number



&#x20;   error\_handling:

&#x20;     - Refuse when the question is not covered by the documents.

&#x20;     - Refuse when multiple documents would need to be combined.

&#x20;     - Refuse when the system cannot establish a safe single-source answer.

&#x20;     - Preserve all conditions from the selected source section.

&#x20;     - Never invent missing policy information.

