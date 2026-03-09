# UC-0B — Summary That Changes Meaning · skills.md

## Skill: read_policy_text

### Purpose
Read a `.txt` policy file and return content as string.

```python
read_policy_text(filepath: str) -> str
```

---

## Skill: extract_clauses

### Purpose
Parse policy text and return list of numbered clauses.

```python
extract_clauses(text: str) -> list[dict]
# Returns: [{clause_number, clause_text}, ...]
```

### Rule
A clause starts with a number followed by `.` or `)` — e.g. `1.`, `2)`, `Clause 3:`

---

## Skill: summarise_clause

### Purpose
Summarise a single clause faithfully — preserving all numbers, dates, conditions.

```python
summarise_clause(clause_text: str) -> str
```

### Constraints
- Do NOT drop any numeric value
- Do NOT change "must" to "may" or "should"
- Do NOT infer rules not stated
- Output: 1–3 sentences

---

## Skill: write_summary_file

### Purpose
Write all clause summaries to `summary_hr_leave.txt`.

```python
write_summary_file(filepath: str, summaries: list[str])
```

---

## CRAFT Notes
- **C**ontext: HR Leave policy, civic org internal doc
- **R**ole: Faithful summariser — not an interpreter
- **A**ction: Extract clauses → summarise each → write file
- **F**ormat: Plain text, one paragraph per clause
- **T**one: Neutral, precise, no softening
