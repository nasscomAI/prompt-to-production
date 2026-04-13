# UC-X Skills

## Skill: retrieve_documents

### Input
- policy_dir: Path to directory containing policy documents

### Output
Dictionary with:
- documents: List of document objects with {name, sections}
- index: Searchable index by document and section

### Logic
1. Load all three policy files:
   - policy_hr_leave.txt
   - policy_it_acceptable_use.txt
   - policy_finance_reimbursement.txt
2. For each document:
   - Parse into sections with numbers and headings
   - Extract numbered clauses within each section
   - Build searchable index
3. Return structured data for querying

### Example Output
```python
{
    "documents": [
        {
            "name": "policy_hr_leave.txt",
            "title": "EMPLOYEE LEAVE POLICY",
            "sections": [
                {
                    "number": "2.3",
                    "text": "Employees must submit a leave application..."
                }
            ]
        }
    ],
    "index": {
        "policy_hr_leave.txt": {
            "2.3": "Employees must submit...",
            "2.4": "Leave applications must..."
        }
    }
}
```

---

## Skill: answer_question

### Input
- question: User's question string
- documents: Output from retrieve_documents

### Output
String with answer and citation OR refusal template

### Logic
1. **Search Phase**
   - Convert question to lowercase for keyword matching
   - Search all documents for relevant sections
   - Track which documents contain relevant information
   - Build list of matching sections with document names

2. **Decision Phase**
   - Count how many documents have relevant information
   - If 0 documents: Use refusal template
   - If 1 document: Proceed to answer from that document
   - If 2+ documents: Check for cross-document blending risk
     - If question can be answered from single most relevant document: Use that
     - If answer would require blending: Use refusal template

3. **Answer Generation Phase**
   - Extract relevant section(s) from chosen document
   - Format answer: "According to [document_name] section X.Y: [information]"
   - Do NOT add interpretations or context
   - Do NOT use forbidden hedging phrases

4. **Validation Phase**
   - Scan answer for forbidden phrases:
     - "while not explicitly"
     - "typically"
     - "generally"
     - "it is common practice"
   - If found, rewrite to remove hedging or use refusal template

### Refusal Template (Use Exactly)
```
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR Department for guidance.
```

### Example Interactions

**Question:** "Can I carry forward unused annual leave?"
**Answer:** "According to policy_hr_leave.txt section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."

**Question:** "Can I use my personal phone for work files from home?"
**Answer:** "According to policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."

**Question:** "What is the company view on flexible working culture?"
**Answer:** "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact HR Department for guidance."

### Keyword Mapping for Search
- Leave, vacation, time off → policy_hr_leave.txt
- Computer, laptop, software, device, phone, email → policy_it_acceptable_use.txt
- Expense, reimbursement, travel, allowance, claim → policy_finance_reimbursement.txt
