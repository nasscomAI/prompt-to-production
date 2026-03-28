# skills.md — UC-X: Ask My Documents

## Skill Set for DocuBot

---

### Skill 1: Document Loader

**Name:** `load_policy_documents`  
**Purpose:** Load all `.txt` policy files from the `data/policy-documents/` directory into memory as a dictionary keyed by filename.

**Input:** Directory path  
**Output:** `dict` — `{ "policy_hr_leave.txt": "<full text>", ... }`

**Failure Guard:**  
- If directory is missing → raise clear error  
- If a file is empty → skip with warning  

```python
def load_policy_documents(directory: str) -> dict:
    """Load all .txt files from the given directory."""
```

---

### Skill 2: Section Retriever

**Name:** `retrieve_relevant_section`  
**Purpose:** Given a user question and the loaded documents, find the single most relevant document and extract the best matching section (paragraph or contiguous lines).

**Input:** `question: str`, `documents: dict`  
**Output:** `tuple(doc_name: str, section_text: str)` — single source only

**Method:**  
1. Tokenise the question into keywords  
2. Score each document by keyword hit count  
3. Select the top-scoring document only (no blending)  
4. Extract the highest-scoring paragraph from that document  

**Failure Guard:**  
- If no document scores > 0 → return `("NOT_FOUND", "")`  

```python
def retrieve_relevant_section(question: str, documents: dict) -> tuple:
    """Return (doc_name, section_text) from the single best-matching document."""
```

---

### Skill 3: Answer Generator

**Name:** `generate_answer`  
**Purpose:** Call the Claude API with the retrieved section as context and the user's question. Instruct the model to answer **only** from the provided context.

**Input:** `question: str`, `context: str`, `doc_name: str`  
**Output:** `str` — formatted answer with attribution

**Prompt Rules (hard-coded):**  
- "Answer ONLY using the context below. Do not use general knowledge."  
- "If the answer is not in the context, say 'Not found in the document.'"  
- "Do not combine information from multiple sources."  

**Failure Guard:**  
- If API call fails → return error message, do not crash  
- If model returns empty → return "No answer generated."  

```python
def generate_answer(question: str, context: str, doc_name: str) -> str:
    """Call Claude API and return answer attributed to doc_name."""
```

---

### Skill 4: Response Formatter

**Name:** `format_response`  
**Purpose:** Wrap the raw LLM answer with clear attribution metadata for the user.

**Input:** `answer: str`, `doc_name: str`  
**Output:** `str` — formatted for terminal display

**Format:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer:
<answer text>

Source: <doc_name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Skill 5: Not-Found Handler

**Name:** `handle_not_found`  
**Purpose:** When `retrieve_relevant_section` returns `NOT_FOUND`, return a user-friendly message instead of a blank or hallucinated response.

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer: This question could not be answered from the loaded policy documents.
Please contact HR/IT/Finance directly for this query.

Source: Not found in any loaded document
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Skill Composition Flow

```
User Question
     │
     ▼
load_policy_documents()   ← runs once at startup
     │
     ▼
retrieve_relevant_section()  ← scores docs, returns single best source
     │
     ├── NOT_FOUND ──► handle_not_found()
     │
     ▼
generate_answer()   ← LLM call with hard "answer only from context" rule
     │
     ▼
format_response()   ← wraps answer with source citation
     │
     ▼
Print to terminal
```

---

## Single-Source Enforcement Rule

> **One question → One document → One answer.**  
> The retriever selects the top-1 scoring document only.  
> The LLM prompt explicitly forbids cross-document synthesis.  
> Attribution is mandatory on every response.
