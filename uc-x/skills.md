### Skill 1: retrieve_documents

**Description**: Accesses the file system to read policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt. It partitions the text into a structured index using regular expressions to identify major headings and subsection IDs (e.g., 2.1, 3.2).

**Input**: Directory path containing the three .txt policy files.

**Output**: A structured dictionary or object where keys are filenames and values are lists of subsections containing the ID and the raw text.

**Error Handling**: If a file is missing, the skill logs a warning but continues indexing the remaining files to ensure partial availability.

---

### Skill 2: answer_question

**Description**: Performs a keyword-weighted search across the indexed policy documents to find the most relevant single subsection. It includes a "Hard-Override" layer to prevent document blending.

**Input**: User query string.

**Output**: A single-source string containing the relevant policy text followed by a mandatory citation: (Source: [Document Name] Section [X.X]).

**Enforcement Logic**:

1. **Single Source Selection**: If multiple documents match, the skill must select the most restrictive or relevant single document (e.g., IT for device questions). It is forbidden from merging text from two different sources.
2. **Refusal Trigger**: If no subsection meets a minimum relevance threshold, or if the question is about "culture" or "general practices," it returns the Verbatim Refusal Template.
3. **Verbatim Mapping**: For questions regarding personal devices, it specifically maps to IT Section 3.2 to ensure "classified or sensitive data" terminology is used.
