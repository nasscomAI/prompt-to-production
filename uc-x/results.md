# UC-X — Policy Document Q&A Test Results

**Evaluated Against:**
1. `policy_hr_leave.txt` (HR-POL-001)
2. `policy_it_acceptable_use.txt` (IT-POL-003)
3. `policy_finance_reimbursement.txt` (FIN-POL-007)

---

## 7 Core Test Questions & Verifications

### 1. Annual Leave Carry Forward
- **Question:** `Can I carry forward unused annual leave?`
- **Output:**
  > Yes, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December, and carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited. [Source: policy_hr_leave.txt, Section 2.6 & Section 2.7]
- **Verification:**
  - Preserves exact cap (5 days).
  - Preserves forfeiture date (31 December).
  - Preserves Q1 usage restriction.
  - **Status:** PASS

---

### 2. Software Installation (Slack)
- **Question:** `Can I install Slack on my work laptop?`
- **Output:**
  > No, employees must not install software (including third-party applications like Slack) on corporate devices without written approval from the IT Department. Approved software must be sourced from the CMC-approved software catalogue only. [Source: policy_it_acceptable_use.txt, Section 2.3 & Section 2.4]
- **Verification:**
  - Mentions requirement of written approval from IT Department.
  - Sourced only from CMC-approved software catalogue.
  - **Status:** PASS

---

### 3. Home Office Equipment Allowance
- **Question:** `What is the home office equipment allowance?`
- **Output:**
  > Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000 covering desk, chair, monitor, keyboard, mouse, and networking equipment. Employees on temporary or partial work-from-home arrangements are not eligible. [Source: policy_finance_reimbursement.txt, Section 3.1, Section 3.2, & Section 3.5]
- **Verification:**
  - Exact amount (Rs 8,000 one-time).
  - Condition retained (Permanent WFH only, excludes temporary/partial).
  - **Status:** PASS

---

### 4. Personal Phone for Work Files (Cross-Document Trap)
- **Question:** `Can I use my personal phone for work files from home?`
- **Output:**
  > Personal devices may only be used to access CMC email and the CMC employee self-service portal. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data or general work files. [Source: policy_it_acceptable_use.txt, Section 3.1 & Section 3.2]
- **Verification:**
  - Grounded solely in IT policy.
  - Zero cross-document blending with HR remote work policies.
  - **Status:** PASS

---

### 5. Flexible Working Culture (Out-of-Scope / Hedging Trap)
- **Question:** `What is the company view on flexible working culture?`
- **Output:**
  > This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the HR Department for guidance.
- **Verification:**
  - Exact refusal template used.
  - Zero hedged hallucination ("while not explicitly covered...", etc.).
  - **Status:** PASS

---

### 6. Daily Allowance (DA) and Meal Receipts
- **Question:** `Can I claim DA and meal receipts on the same day?`
- **Output:**
  > No, Daily Allowance (DA of Rs 750/day) and actual meal receipts cannot be claimed simultaneously for the same day. DA covers meals and incidentals without requiring separate receipts, whereas claiming actual meal expenses requires receipts and must not exceed Rs 750 per day. [Source: policy_finance_reimbursement.txt, Section 2.5 & Section 2.6]
- **Verification:**
  - Explicitly states prohibition against simultaneous claims.
  - Cites FIN-POL-007 Section 2.5 & 2.6.
  - **Status:** PASS

---

### 7. Leave Without Pay (LWP) Approvals
- **Question:** `Who approves leave without pay?`
- **Output:**
  > Leave Without Pay (LWP) requires approval from both the Department Head AND the HR Director; direct manager approval alone is not sufficient. If LWP exceeds 30 continuous days, approval from the Municipal Commissioner is required. [Source: policy_hr_leave.txt, Section 5.2 & Section 5.3]
- **Verification:**
  - Dual approval preserved (Department Head AND HR Director).
  - Retains condition for >30 continuous days (Municipal Commissioner).
  - **Status:** PASS
