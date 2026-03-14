# UC-0B Summary That Changes Meaning — Skills

## Skills Overview

This module defines the operational skills used by the **Policy Summary Validator Agent** to generate and validate policy summaries while ensuring meaning preservation.

---

# 1. Policy Loader

**name:** `load_policy`

**description:**
Loads policy text from a given file path.

**input:**
File path (`str` or `Path`)

**output:**
Raw policy text (`str`)

**error handling:**

* Raises `FileNotFoundError` if file does not exist
* Returns empty string if file cannot be parsed

---

# 2. Extract Critical Elements

**name:** `extract_critical_elements`

**description:**
Extracts important policy information using regex pattern matching.

Extracted elements include:

* numeric limits
* deadlines
* mandatory obligations
* policy scope

**input:**
Policy text (`str`)

**output:**

```
{
 numbers: [],
 deadlines: [],
 obligations: [],
 scope: []
}
```

**error handling:**
Empty input returns empty collections.

---

# 3. Generate Summary

**name:** `generate_summary`

**description:**
Creates a **2–5 sentence policy summary** by extracting key sections and combining them into concise statements.

The summary must include:

* policy scope
* at least one numeric entitlement or limit
* mandatory procedure if present

**input:**
Policy text (`str`)

**output:**
Summary string

**error handling:**

```
"Unable to summarise: empty policy."
```

---

# 4. Validate Summary

**name:** `validate_summary`

**description:**
Ensures the generated summary preserves the original policy meaning.

Checks performed:

* presence of critical numbers
* presence of mandatory procedures
* presence of scope and obligations

**input:**

```
policy_text (str)
summary (str)
critical_elements (dict)
```

**output:**

```
{
 valid: bool,
 risky: bool,
 omitted_critical: []
}
```

**error handling:**

If summary or policy text is empty:

```
valid = false
risky = true
```

---

# Validation Rules

| Rule                  | Check                                       |
| --------------------- | ------------------------------------------- |
| Summary length        | 2–5 sentences                               |
| No fabrication        | Only information present in policy          |
| Numeric limits        | At least one key numeric value mentioned    |
| Mandatory obligations | Must preserve requirement language          |
| Risk flag             | Triggered when critical information missing |

---

# Critical Elements Examples

Numeric limits:

```
18 days
12 days
30 days
Rs 500
Rs 800
Rs 3500
```

Mandatory procedures:

```
must submit
requires approval
within X days
```

Scope examples:

```
permanent employees
contractual staff
grade C and above
```

---

# Example Inputs / Outputs

### Input (policy excerpt)

```
2.1 Each permanent employee is entitled to 18 days of paid annual leave.
2.3 Employees must submit a leave application at least 14 calendar days in advance.
```

---

### Valid Summary

```
{
 "policy_name": "policy_hr_leave.txt",
 "summary": "The policy governs leave for permanent employees. Employees receive 18 days of paid annual leave and 12 days of sick leave per year. Leave applications must be submitted at least 14 days in advance.",
 "valid": true,
 "risky": false,
 "omitted_critical": []
}
```

---

### Risky Summary

```
{
 "policy_name": "policy_hr_leave.txt",
 "summary": "Employees receive annual and sick leave benefits.",
 "valid": false,
 "risky": true,
 "omitted_critical": [
  "18 days annual leave",
  "14 days advance application",
  "12 days sick leave"
 ]
}
```

---

# AI-Assisted Prompt (for development)

```
Does this summary accurately reflect the policy?
Check the following:

1. policy scope
2. numeric limits
3. mandatory procedures

List any missing critical information.
```

---

# CRAFT Iteration

This skill set was refined using the **CRAFT loop**:

1. Create initial summarization rules
2. Run summary generation
3. Analyze missing elements
4. Fix extraction and validation logic
5. Test again with multiple policy examples

This iterative approach improves **accuracy and reliability** of policy summaries.
