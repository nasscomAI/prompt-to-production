# UC-X — Ask My Documents · skills.md

## Skill: load_document

### Purpose
Load a policy document and return its text content.

```python
load_document(filepath: str) -> str
```

---

## Skill: search_document

### Purpose
Search document text for sentences/paragraphs relevant to a question using keyword matching.

```python
search_document(text: str, question: str) -> list[str]
# Returns: list of matching passages (up to 3)
```

### Algorithm
1. Tokenise question into keywords (strip stopwords)
2. Score each sentence by keyword overlap
3. Return top-3 scoring sentences

---

## Skill: answer_from_passage

### Purpose
Given a passage and question, return a grounded answer.

```python
answer_from_passage(passage: str, question: str, source_doc: str) -> dict
```

### Rules
- Answer must come only from the passage
- If no passage found: return `found=False`, answer=`"Not found in {source_doc}"`
- Include `source_clause` field with verbatim passage

---

## Skill: run_qa_loop

### Purpose
Interactive loop — prompt user for question + document choice, return answer.

---

## CRAFT Notes
- **C**ontext: Policy QA for civic org employees
- **R**ole: Faithful retriever — not a reasoner or guesser
- **A**ction: Load doc → search → answer with citation
- **F**ormat: Structured dict response
- **T**one: Precise, attributed, no hallucination

## Anti-Pattern (what NOT to do)
```python
# WRONG — blends multiple docs
for doc in all_docs:
    passages.extend(search_document(doc, question))  # ← cross-doc blending

# CORRECT — single source
passages = search_document(target_doc_text, question)
```
