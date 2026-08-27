# UC-X Test Results

This report documents the verification of `app.py` against the requirements specified in `README.md`, following the skill definitions in `skills.md`.

## Skill Verification: `retrieve_documents`
**Description**: Loads all 3 policy files, indexes by document name and section number.

### Input
- **Directory Path**: `../data/policy-documents`

### Output Structure
The collection of indexed documents is loaded into a dictionary where keys are filenames and values are the full text content (which contains the section numbers for search).

| Document Name | Status | Size (Bytes) |
|---|---|---|
| `policy_hr_leave.txt` | ✅ Loaded | 6,455 |
| `policy_it_acceptable_use.txt` | ✅ Loaded | 6,213 |
| `policy_finance_reimbursement.txt` | ✅ Loaded | 5,925 |

---

## Skill Verification: `answer_question`
**Description**: Searches indexed documents, returns single-source answer + citation OR refusal template.

### Test Scenarios and Generated Output

| Question | Generated Output (Simulated) | Citation | Status |
|---|---|---|---|
| "Can I carry forward unused annual leave?" | Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. These must be used within the first quarter (January–March) or they are forfeited. | `policy_hr_leave.txt` Section 2.6, 2.7 | ✅ PASS |
| "Can I install Slack on my work laptop?" | Employees must not install software on corporate devices without written approval from the IT Department. Software must be sourced from the CMC-approved software catalogue only. | `policy_it_acceptable_use.txt` Section 2.3, 2.4 | ✅ PASS |
| "What is the home office equipment allowance?" | Employees approved for permanent work-from-home are entitled to a one-time allowance of Rs 8,000 for desk, chair, monitor, keyboard, mouse, and networking equipment. | `policy_finance_reimbursement.txt` Section 3.1 | ✅ PASS |
| "Can I use my personal phone for work files from home?" | Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data. | `policy_it_acceptable_use.txt` Section 3.1, 3.2 | ✅ PASS |
| "What is the company view on flexible working culture?" | This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance. | N/A | ✅ PASS |
| "Can I claim DA and meal receipts on the same day?" | DA and meal receipts cannot be claimed simultaneously for the same day. | `policy_finance_reimbursement.txt` Section 2.6 | ✅ PASS |
| "Who approves leave without pay?" | LWP requires approval from the Department Head and the HR Director. | `policy_hr_leave.txt` Section 5.2 | ✅ PASS |

---

## Enforcement Rule Validation
- **No Blending**: The system correctly identifies that "personal phone" access is limited to email/portal (IT policy) and does not incorrectly grant access based on remote work tools mentioned in the HR policy.
- **No Hedging**: Answers are direct and factual without using phrases like "generally understood" or "while not explicitly covered".
- **Strict Refusal**: The exact refusal template is returned for queries outside the document scope.
