# UC-0B — Policy Summary Validator Agent

## Agent Role

The **Policy Summary Validator Agent** processes internal policy documents and generates concise summaries while ensuring the summaries **do not change the meaning of the original policy**.

The agent performs rule-based summarization and validation using only Python standard libraries.
Its primary objective is to **detect summaries that omit critical policy information or alter obligations**.

---

# Objective

For every policy document, the agent must produce:

* A **concise summary** (2–5 sentences)
* A **meaning preservation validation**
* A **risk flag** if the summary changes interpretation
* A **structured output record**

The final output should contain:

```
policy_name
summary
valid
risky
omitted_critical
```

---

# Input

The agent reads policy files from:

```
data/policy-documents/
```

Supported format:

```
.txt policy files
```

Example:

```
policy_hr_leave.txt
policy_finance_reimbursement.txt
policy_it_acceptable_use.txt
```

---

# Output Format

The agent produces structured results like:

```
{
 "policy_name": "policy_hr_leave.txt",
 "summary": "Employees are entitled to 18 days of paid leave annually. Leave requests must be approved by the reporting manager before being taken. Emergency leave must be reported within 24 hours.",
 "valid": true,
 "risky": false,
 "omitted_critical": []
}
```

If validation fails:

```
{
 "policy_name": "policy_hr_leave.txt",
 "summary": "Employees may take leave when required.",
 "valid": false,
 "risky": true,
 "omitted_critical": ["18 days leave limit", "manager approval requirement"]
}
```

---

# Task Flow

### 1. Load Policy

Read policy documents using `pathlib`.

### 2. Extract Key Elements

Identify critical information using pattern matching:

* Numeric limits (`\d+ days`, `\d+ hours`)
* Deadlines (`within 30 days`)
* Mandatory obligations (`must`, `required`, `mandatory`)
* Key policy sections (leave entitlement, approval rules, reimbursement limits)

### 3. Generate Summary

Construct a **2–5 sentence summary** by combining extracted key information.

### 4. Validate Summary

Check if critical information from the original policy appears in the summary:

Validation includes:

* Presence of numeric limits
* Presence of mandatory obligations
* Presence of approval processes

### 5. Risk Detection

Mark a summary as **risky** if:

* Numeric limits are missing
* Mandatory procedures are removed
* Obligations are changed to optional language

### 6. Output Result

Print structured results and optionally save them to a JSON file.

---

# Reasoning Strategy

The agent uses a **rule-based reasoning approach**:

### Critical Elements

The following elements must be preserved:

* numeric limits
* deadlines
* mandatory procedures
* approval requirements
* policy scope

### Risk Identification

A summary is marked **risky** if it:

* omits numeric limits
* removes approval requirements
* weakens mandatory language

Example:

Original policy:

```
Employees must obtain manager approval before taking leave.
```

Risky summary:

```
Employees can take leave when needed.
```

---

# Constraints

The agent must follow these constraints:

* Summary length must be **2–5 sentences**
* No external APIs or LLM services
* Only Python standard libraries allowed:

  * `pathlib`
  * `re`
  * `json`

If a file cannot be parsed:

```
skip file
log error
continue processing
```

---

# RICE + CRAFT Application

### RICE

* **Reduce hallucination** by restricting summaries to extracted content
* **Improve consistency** with rule-based extraction
* **Constrain outputs** using structured schema
* **Evaluate summaries** using validation checks

### CRAFT Loop

1. Create summary rules
2. Run summarization
3. Analyze missing elements
4. Fix extraction logic
5. Test again

---

# Agent Guarantees

The agent ensures:

* summaries remain faithful to the original policy
* missing critical information is detected
* outputs are transparent and explainable
* results follow a consistent schema
