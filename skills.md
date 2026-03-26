# skills.md — UC-0B: Summary That Changes Meaning

## Skill Set for PolicySummaryAgent

---

### Skill 1: `read_policy_document`

**Purpose:** Load and parse a plain-text HR policy document from disk.  
**Input:** File path to `.txt` policy document  
**Output:** Raw text string  

**Logic:**
- Open file with UTF-8 encoding
- Strip leading/trailing whitespace
- Return full text

**Failure handling:**
- If file not found → raise `FileNotFoundError` with clear message
- If file is empty → raise `ValueError("Policy document is empty")`

---

### Skill 2: `count_clauses`

**Purpose:** Count the number of numbered clauses in the source document to enable completeness checking.  
**Input:** Raw policy text  
**Output:** Integer count of clauses  

**Logic:**
- Use regex to find patterns like `1.`, `2.`, `1)`, `(a)`, `Section 1`, `Clause 1`
- Return total count

---

### Skill 3: `summarise_with_llm`

**Purpose:** Send the policy text to an LLM with a strict summarisation prompt that enforces completeness and meaning-preservation.  
**Input:** Raw policy text, document title  
**Output:** Structured summary string  

**Prompt strategy (CRAFT loop):**
- **C**ontext: "You are summarising an HR policy for employees who will rely on it legally."
- **R**ole: "You are a precise policy summarisation specialist."
- **A**ction: "Summarise every numbered clause. Do not omit, soften, or merge clauses."
- **F**ormat: "Output section-by-section. Mark conditions with [CONDITION]."
- **T**one: "Neutral and precise. No editorialising."

**Enforcement rules embedded in prompt:**
1. Every clause must appear
2. Obligations (`must`, `shall`, `will not`) must stay obligations
3. Penalties must not be softened
4. Conditions and exceptions must be preserved

---

### Skill 4: `verify_completeness`

**Purpose:** Check that the summary covers all clauses found in the source document.  
**Input:** Source clause count, summary text  
**Output:** `PASS` or `FAIL` with details  

**Logic:**
- Count clause markers in summary
- Compare to source clause count
- If summary count < source count → `FAIL` with list of potentially missing clauses

---

### Skill 5: `write_summary_file`

**Purpose:** Write the final verified summary to disk as `summary_hr_leave.txt`.  
**Input:** Summary string, output file path  
**Output:** Confirmation message  

**Logic:**
- Open output path for writing (UTF-8)
- Write summary string
- Print confirmation with file path and character count

---

### Skill 6: `detect_meaning_drift`

**Purpose:** Scan the generated summary for known softening patterns that indicate meaning drift.  
**Input:** Summary text  
**Output:** List of warnings (empty list = clean)  

**Patterns to flag:**

| Risky phrase in summary | What it likely softened |
|------------------------|------------------------|
| "may face" | "will be terminated" |
| "should submit" | "must submit" |
| "encouraged to" | "required to" |
| "consider" | "must" |
| "generally" | a specific rule |
| "etc." | a complete list |

**Output format:**
```
[DRIFT WARNING] Line 12: "should submit" — original may have said "must submit"
```

---

## Skill Execution Order

```
read_policy_document
        ↓
count_clauses
        ↓
summarise_with_llm
        ↓
detect_meaning_drift  ← re-prompt if warnings found
        ↓
verify_completeness   ← re-prompt if FAIL
        ↓
write_summary_file
```
