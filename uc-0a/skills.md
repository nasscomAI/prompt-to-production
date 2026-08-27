# UC-0A — Complaint Classifier Skills

## Skill 1: `classify_complaint`
**Input**: One complaint row (dict with keys: complaint_id, description, etc.)
**Output**: Dict with {category, priority, reason, flag}

**Algorithm**:
```
1. Extract description text
2. Scan for severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
   - If found AND contextually positive (threat/risk): priority = "Urgent"
   - Else: priority = "Standard" (default)
3. Classify category by matching complaint type:
   - Pothole: "pothole" OR "hole" OR "sinking" OR "cracked" (in road context)
   - Flooding: "flood" OR "water" OR "rain" OR "waterlogged" OR "submerged"
   - Streetlight: "light" OR "street light" OR "dark" (in lighting context)
   - Waste: "garbage" OR "waste" OR "trash" OR "litter" OR "bin"
   - Noise: "noise" OR "music" OR "sound" OR "loud"
   - Road Damage: "road" AND ("crack" OR "damage" OR "deteriorat") [not pothole-specific]
   - Heritage Damage: "heritage" OR "old city" OR "historic"
   - Heat Hazard: "heat" OR "temperature" OR "sun" [with hazard context]
   - Drain Blockage: "drain" OR "blocked" OR "blockage" OR "manhole"
   - Other: If no clear match
4. Generate reason: cite specific keywords from description that triggered classification
5. If category is ambiguous (multiple strong matches), set flag="NEEDS_REVIEW"
```

**Severity Keywords Check**:
- Trigger Urgent: "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
- Context check: If phrase is negative (e.g., "no injury reported"), still flag as NEEDS_REVIEW but set priority to Standard

---

## Skill 2: `batch_classify`
**Input**: Path to input CSV (../data/city-test-files/test_[city].csv)
**Output**: Path to output CSV (results_[city].csv) with columns: complaint_id, category, priority, reason, flag

**Algorithm**:
```
1. Read input CSV
2. For each row:
   - Call classify_complaint(row)
   - Append result to output list
3. Validate all rows:
   - Check for null categories (fill with "Other" only if truly unclassifiable)
   - Check for missing reasons
   - Check for uncategorized urgency (severity keywords without Urgent priority)
4. Write output CSV with header: complaint_id,category,priority,reason,flag
5. Return success message with count of Urgent, Standard, and NEEDS_REVIEW rows
```

---

## Validation Checks (Run After Classification)
1. Row count matches input (15 rows)
2. All categories in allowed list
3. All priorities in [Urgent, Standard, Low]
4. No empty reason fields
5. All severity keyword rows are Urgent (unless NEEDS_REVIEW)
