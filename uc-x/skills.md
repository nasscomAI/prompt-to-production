Skill: retrieve_documents
Purpose:
loads all 3 policy files, indexes by document name and section number

Inputs:
None

Outputs:
Indexed policy documents


Skill: answer_question
Purpose:
searches indexed documents, returns single-source answer + citation OR refusal template

Inputs:
User question
Indexed documents

Outputs:
Single-source answer with citation OR refusal template exactly