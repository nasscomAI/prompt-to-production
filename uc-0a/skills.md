# UC-0A Skills

## Overview

This file defines the executable skills used by the UC-0A complaint
classification agent.

The implementation is deterministic and operates only on the supplied
complaint CSV. It does not use external services, APIs, databases, or
information from other complaint rows.

---

## Skill 1: classify_complaint

### Purpose

Classify a single citizen complaint into the required category and priority
while producing an evidence-based reason and ambiguity flag.

### Input

A single CSV row containing at least:

- `description`

The row may also contain additional fields such as:

- `complaint_id`
- `days_open`
- `location`
- other original fields

### Output

The original row unchanged plus:

- `category`
- `priority`
- `reason`
- `flag`

### Allowed Categories

The category must be exactly one of:

1. Pothole
2. Flooding
3. Streetlight
4. Waste
5. Noise
6. Road Damage
7. Heritage Damage
8. Heat Hazard
9. Drain Blockage
10. Other

### Allowed Priorities

The priority must be exactly one of:

- Urgent
- Standard
- Low

### Severity Rule

The following case-insensitive keywords are safety-critical:

- injury
- child
- school
- hospital
- ambulance
- fire
- hazard
- fell
- collapse

If any severity keyword occurs in the description:

```text
priority = Urgent

```

### Error handling

If `description` is missing or empty, the skill should return `category` = `Other`,
`priority` = `Standard`, `reason` = "No description provided.", and `flag` = `NEEDS_REVIEW`.
