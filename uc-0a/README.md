# UC-0A — Complaint Classifier

## Overview

UC-0A classifies citizen complaints into a fixed set of categories and assigns a priority level.

The classifier is designed to prevent:

- Taxonomy drift
- Severity blindness
- Missing justification
- Hallucinated sub-categories
- False confidence on ambiguous complaints

---

## Input

The classifier accepts a CSV file containing citizen complaints.

Expected columns:

```text
complaint_id
date_raised
city
ward
location
description
reported_by
days_open