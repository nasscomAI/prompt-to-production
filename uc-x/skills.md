# UC-X Ask My Documents Skills

## Defined Skills

### 1. `retrieve_documents`
- **Description**: Loads all 3 policy text documents (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`) into an indexed structure grouped by file name and section number.
- **Input**: List of document file paths.
- **Output**: Indexed policy section dictionary.

### 2. `answer_question`
- **Description**: Searches indexed document sections for exact keyword matches. Returns a single-source answer with document name and section citation, or returns the exact Refusal Template if unsupported or if query requires document blending.
- **Input**: Query string + indexed policy document dictionary.
- **Output**: Formatted answer string.
