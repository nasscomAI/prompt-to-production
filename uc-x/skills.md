# UC-X Ask My Documents — Skills Definition

## Skill 1: `retrieve_documents`

**Purpose**: Loads all 3 policy text documents and indexes them by document name and section number for fast lookup.

**Input**: List of file paths to the 3 policy documents.

**Output**: A nested dictionary:
```
{
  "policy_hr_leave.txt": {
    "1.1": "This policy governs...",
    "2.3": "Employees must submit...",
    ...
  },
  "policy_it_acceptable_use.txt": { ... },
  "policy_finance_reimbursement.txt": { ... }
}
```

**Behaviour**:
- Parses each document using regex to split on clause numbers (e.g., `2.3`, `5.2`).
- Normalizes whitespace within each clause.
- Reports total sections indexed per document.

**Error handling**: Skips missing files with a warning. Returns empty dict for unparseable documents.

---

## Skill 2: `answer_question`

**Purpose**: Searches the indexed document sections for a relevant answer to the user's question. Returns either a single-source cited answer or the exact Refusal Template.

**Input**: Query string + indexed document dictionary from `retrieve_documents`.

**Output**: Formatted answer string in one of two forms:
1. `[document_name - Section X.Y]\nAnswer text from that section`
2. The verbatim Refusal Template (if not covered or cross-document blending required)

**Search strategy**:
- Keyword-based matching against query to identify the most relevant document and section.
- Priority-ordered rules map common query patterns to specific sections.
- Cross-document detection: if a query matches sections in multiple documents, returns only the single most relevant section, never a blend.

**Enforcement checks**:
- Before returning, verifies the answer cites exactly one document.
- Checks for banned hedging phrases and strips them if found.
- Defaults to Refusal Template for any unrecognized query.

**Error handling**: Returns Refusal Template for empty queries or queries with no document match.
