# Skills

## retrieve_documents

Input:

* All policy text files

Output:

* Indexed documents with section numbers

Responsibilities:

* Load all documents.
* Preserve section numbers.
* Index by document name.

---

## answer_question

Input:

* User question

Output:

* Single-source answer with citation OR refusal template.

Rules:

* Never combine documents.
* Always cite document and section.
* Use refusal template if answer is unavailable.

