# UC-X Civic Tech Assistant — Skills

## Skills

### 1. Intent Detection

- **name**: `detect_intent`
- **description**: Determines user intent from natural language question.
- **input**: User question (str)
- **output**: Dict with `intent` (budget | policy | complaint | unknown), `entities` (ward, category, topic)
- **error_handling**: Empty input → intent: unknown. Unclear → intent: unknown, suggest options.

### 2. Budget Analyzer

- **name**: `analyze_budget`
- **description**: Answers budget questions using ward_budget.csv.
- **input**: Question (str), optional ward, optional category
- **output**: Dict with answer, reasoning, data_sources, overspend_flags
- **error_handling**: Missing file → "No budget data available."

### 3. Policy Lookup

- **name**: `lookup_policy`
- **description**: Finds relevant policy content by topic.
- **input**: Topic (str), e.g., "leave", "reimbursement", "IT"
- **output**: Dict with policy_name, excerpt, reasoning
- **error_handling**: No match → "No matching policy found."

### 4. Complaint Summary

- **name**: `summarise_complaints`
- **description**: Classifies complaints and returns category breakdown.
- **input**: Optional city filter
- **output**: Dict with category_counts, sample_complaints, reasoning
- **error_handling**: No files → "No complaint data available."

### 5. Synthesise Response

- **name**: `synthesise_response`
- **description**: Combines analyzer outputs into a structured response.
- **input**: intent, analyzer results
- **output**: Dict with answer, reasoning, data_sources
- **error_handling**: Always produce a response; never return empty.

---

## Prompts (for intent detection)

- Budget: "ward", "budget", "overspend", "spending", "roads", "drainage", "waste", "streetlight"
- Policy: "policy", "leave", "reimbursement", "IT", "acceptable use", "expense"
- Complaint: "complaint", "complaints", "citizen", "report"

---

## Example Inputs/Outputs

**Input**: "Is my ward budget overspending on roads?"

**Output**:
```json
{
  "intent": "budget",
  "answer": "Yes. Several wards show overspending on Roads & Pothole Repair. For example, Ward 2 Shivajinagar spent 19.7L against 15.8L budget in June 2024 (24.7% over).",
  "reasoning": "Loaded ward_budget.csv. Filtered for Roads & Pothole Repair. Compared actual_spend vs budgeted_amount. Flagged rows where actual > budget * 1.2.",
  "data_sources": ["data/budget/ward_budget.csv"]
}
```

---

**Input**: "What is the annual leave entitlement?"

**Output**:
```json
{
  "intent": "policy",
  "answer": "Permanent employees get 18 days paid annual leave per calendar year. Leave accrues at 1.5 days per month.",
  "reasoning": "Searched policy_hr_leave.txt for 'annual leave'. Extracted Section 2.",
  "data_sources": ["data/policy-documents/policy_hr_leave.txt"]
}
```
