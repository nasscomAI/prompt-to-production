# Skills

## classify_complaint

### Input
One complaint description.

### Output
- category
- priority
- reason
- flag

### Rules
- Use only approved categories.
- Detect severity keywords.
- Generate a one-sentence reason.
- Flag ambiguous complaints.

---

## batch_classify

### Input
CSV file.

### Process
- Read each complaint.
- Classify it.
- Save results.

### Output
CSV containing:
- category
- priority
- reason
- flag
