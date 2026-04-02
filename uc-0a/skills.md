# Skills: Complaint Classification

## classify_complaint

### Input
One complaint description string

### Output
- category (must be one of allowed values)
- priority (Urgent / Standard / Low)
- reason (one sentence citing words from input)
- flag (NEEDS_REVIEW or blank)

### Allowed Categories (STRICT)
Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other

### Severity Keywords (MANDATORY)
injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

### Logic
1. Convert complaint text to lowercase
2. Match keywords to assign category from allowed list only
3. If no category keyword found → assign "Other" and set flag = NEEDS_REVIEW
4. Check severity keywords:
   - If any present → priority = Urgent
   - Else if moderate indicators → Standard
   - Else → Low
5. Generate reason using exact words from complaint
6. Ensure no invalid category or priority values are returned

---

## batch_classify

### Input
CSV file with complaint descriptions

### Process
- Read CSV using DictReader
- For each row:
  - Call classify_complaint
  - Handle errors without crashing
- Continue processing even if some rows fail

### Output
New CSV with columns:
- complaint_id
- category
- priority
- reason
- flag

### Error Handling
- If row processing fails → assign:
  - category = Other
  - priority = Low
  - flag = NEEDS_REVIEW
  - reason = error description