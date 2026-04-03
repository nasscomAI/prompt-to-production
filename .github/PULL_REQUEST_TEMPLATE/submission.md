# Vibe Coding Workshop — Submission PR

**Name:**  
Dhaval Shah
**City / Group:**  
Ahmedabad, Gujarat
**Date:**  
26-03-2026
**AI tool(s) used:**  
Antigravity
---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
- [x] `results_[city].csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Taxonomy Drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> **Enforcement Rule 1:** If the complaint text contains any of the following keywords, the category must be set to the corresponding value:
> - Pothole → Pothole
> - Road damage → Road Damage
> - Streetlight → Streetlight
> - Waste / Garbage → Waste
> - Noise / Music → Noise
> - Flooding / Flood → Flooding
> - Heritage → Heritage Damage
> - Other → Other
> If none of these keywords are present, the category should be set to "Other".

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 12 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — [explain any exceptions]

**Your git commit message for UC-0A:**

> UC-0A Fix Severity blindness & Taxonomy drift: Location took priority over nature and urgency keywords were missing → Added precedence rules, NEEDS_REVIEW flag, and urgency triggers.
> UC-0A Fix Taxonomy Drift: Naive classification was inconsistent → Implemented keyword-based logic with strict reason citation

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Form & Documentation (Clause 2.3): The specific requirement to use Form HR-L1 for leave applications.
Verbal Approval (Clause 2.4): The explicit statement that verbal approval is not valid; only written approval is recognized.
Compensatory Off Encashment (Clause 6.3): The clause stating that compensatory off cannot be encashed (it can only be taken as time off).
Sick/LWP Encashment (Clause 7.3): The explicit prohibition that Sick Leave and Leave Without Pay (LWP) can never be encashed under any circumstances (unlike Annual Leave).
Grievance Exceptions (Clause 8.2): The provision that grievances raised after 10 days might be considered if exceptional circumstances are demonstrated in writing.
Accrual Rate (Clause 2.2): While mentioned, I didn't highlight that annual leave accrues from the date of joining.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No

**Your git commit message for UC-0B:**

> UC-0B Fix Clause omission: Initial prompt might drop multi-condition obligations like 5.2 → Implemented structured clause retrieva
l and explicit condition preservation in app.py

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> === Monthly Total Actual Spend (₹ Lakhs) ===
Period          Total Spend   M-o-M Growth
2024-01              163.10              —
2024-02              163.80          +0.4%
2024-03              154.80          -5.5%
2024-04              159.80          +3.2%
2024-05              163.00          +2.0%
2024-06              190.00         +16.6%
2024-07              219.70         +15.6%
2024-08              233.90          +6.5%
2024-09              233.10          -0.3%
2024-10              188.50         -19.1%
2024-11              161.60         -14.3%
2024-12              162.60          +0.6%

Overall Jan→Dec Growth: -0.3%
  Jan-24: ₹163.10L  →  Dec-24: ₹162.60L

=== Growth by Category (Jan → Dec 2024) ===
Category                       Jan (₹L)   Dec (₹L)     Growth
Drainage & Flooding               43.30      42.70      -1.4%
Parks & Greening                  11.40      11.00      -3.5%
Roads & Pothole Repair            65.60      63.20      -3.7%
Streetlight Maintenance           16.70      18.40     +10.2%
Waste Management                  26.10      27.30      +4.6%

=== Growth by Ward (Jan → Dec 2024) ===
Ward                           Jan (₹L)   Dec (₹L)     Growth
Ward 1 – Kasba                    31.30      32.90      +5.1%
Ward 2 – Shivajinagar             38.60      35.70      -7.5%
Ward 3 – Kothrud                  29.90      31.40      +5.0%
Ward 4 – Warje                    25.40      27.90      +9.8%
Ward 5 – Hadapsar                 37.90      34.70      -8.4%

=== Peak Spend Month: 2024-08 (₹233.90L) ===

=== Full-Year Budget Utilisation ===
  Total Budgeted : ₹2006.40L
  Total Actual   : ₹2193.90L
  Utilisation    : 109.3%
  (Missing data points: 5)

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix Universal aggregation bypass: 'Any' keyword allowed unsupported aggregation → blocked 'Any' keyword and implemented missing YoY logic
> UC-0C Fix Silent null handling: Standard aggrega
tion would ignore the 5 deliberate nulls → Implemented load-time null flagging and explicit formula visibility in app.py

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> Based on the **IT Acceptable Use Policy (IT-POL-003)**, the answer is: **it depends on what "work files" means.**

Here's the breakdown:

### ✅ What you CAN do on a personal phone:
- Access **CMC email**
- Access the **CMC employee self-service portal**

### ❌ What you CANNOT do on a personal phone:
- Access, store, or transmit **classified or sensitive CMC data** (§3.2)
- Connect to the **CMC internal network** — wired or wireless (§3.3)

---

### ⚠️ If you use your personal phone for CMC email, you must:
1. Enable a **PIN or biometric lock** on your device (§3.4)
2. If your phone is **lost or stolen**, report it to the IT helpdesk **within 4 hours** so a remote wipe of CMC data can be performed (§3.5)

---

### 📌 Bottom Line

> If "work files" means **classified or sensitive data** — **No**, you cannot access those on a personal phone, even at home.
>
> If it's just **email or the self-service portal** — **Yes**, but only with a screen lock enabled.

For sensitive work documents, you should use a **CMC-issued corporate device** instead.

**Did it blend the IT and HR policies?**

> No 

**After your fix — what does your system return for this question?**

> Source: policy_it_acceptable_use.txt (Section 3.1)

Personal devices may be used to access CMC email and the CMC employee self-service portal only.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix retrieval bleed and mapping: headers bled into text and LWP acronym was missed → implemented text cleaning and acronym-aware mapping in app.py
> UC-X Fix Cross-document blending: Initial prompt might mix IT and HR permissions for personal devices → Implemented single-source retrieval and strict referral template in app.py

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Enforcement (A) step in the agents.md was the most difficult because it requires to manually anticipate "deceptively smart" AI failures—like Taxonomy Drift(by category precedence), Severity keyword blindness in UC-0A, Cross-document blending, retrieval bleed & mapping for UC-X, and silent null handling, universal aggregation bypass in UC-0C—that aren't obvious until they happen.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The manual Category Precedence and Ambiguity Rule in UC-0A: "To use NEEDS_REVIEW whenever a description matches two or more categories within the same priority level." By default, the AI wants to pick a single "best" category even when the data is split, so forcing it to admit ambiguity via a flag is a critical production-safety feature that requires manual intervention. 

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use RICE + CRAFT to build a production-safe AI agent that can answer questions about own Insurance policies-help to gain clarity on insurance clauses for the end users.

---

## Reviewer Notes *(tutor fills this section)*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | | |
| agents.md quality | | |
| skills.md quality | | |
| CRAFT loop evidence | | |
| Test coverage | | |
| **Total** | **/20** | |

**Badge decision:**
- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________
