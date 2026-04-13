# UC-0A Skills

## Skill: classify_complaint

### Input
Single complaint row with fields: complaint_id, description

### Output
Dictionary with: category, priority, reason, flag

### Logic
1. **Category Classification**
   - Scan description for keywords:
     - "pothole", "tyre damage", "road hole" → Pothole
     - "flood", "waterlogged", "water", "rain" → Flooding
     - "streetlight", "light", "dark", "lamp" → Streetlight
     - "garbage", "waste", "smell", "bins" → Waste
     - "noise", "music", "loud" → Noise
     - "road", "crack", "surface", "manhole" → Road Damage
     - "heritage", "old city" → Heritage Damage
     - "drain", "blocked drain" → Drain Blockage
   - If no clear match → "Other" + flag "NEEDS_REVIEW"

2. **Priority Classification**
   - Check for severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
   - If ANY found → "Urgent"
   - Else if infrastructure issue → "Standard"
   - Else → "Low"

3. **Reason Generation**
   - Extract specific words from description that led to classification
   - Format: "Description mentions [keyword] indicating [category/priority]"

4. **Flag Setting**
   - Set "NEEDS_REVIEW" if:
     - Category is "Other"
     - Multiple categories could apply equally
     - Description is ambiguous
   - Otherwise leave blank

### Example
Input: "Deep pothole near bus stop. School children at risk during morning hours."
Output:
- category: "Pothole"
- priority: "Urgent"
- reason: "Description mentions 'pothole' indicating Pothole category and 'school children' indicating Urgent priority"
- flag: ""

---

## Skill: batch_classify

### Input
- input_file: path to CSV file
- output_file: path for results CSV

### Output
CSV file with classified complaints

### Logic
1. Read input CSV using pandas
2. Initialize empty results list
3. For each row:
   - Extract complaint_id and description
   - Call classify_complaint skill
   - Append result with complaint_id
4. Convert results to DataFrame
5. Write to output CSV with columns: complaint_id, category, priority, reason, flag
6. Return success message with row count
