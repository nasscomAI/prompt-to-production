# skills.md — UC-X Document Q&A System

## Skill 1: `retrieve_documents`
**Purpose**: Load and index the three policy documents by document name and section number.

**Input**: Paths to the three policy documents.

**Output**: A dictionary where keys are tuples of `(document_name, section_number)` and values are the corresponding text.

**Rules**:
- Extract and index all sections from the documents.
- Preserve the exact text of each section.

---

## Skill 2: `answer_question`
**Purpose**: Answer a question based on the indexed policy documents.

**Input**: A user question (e.g., "Can I use my personal phone for work files from home?").

**Output**: A single-source answer with citation or the refusal template.

**Rules**:
- Search the indexed documents for the most relevant section.
- Return a single-source answer with citation or the refusal template.
- Never blend information from multiple documents.