# Skills

## Skill: classify_complaint

### Description
Classifies a single civic complaint into a category, priority, reason, and review flag based on keyword matching against the description text.

### Inputs
| Parameter | Type | Required | Description |
|---|---|---|---|
| description | string | yes | The complaint description text |
| days_open | integer | yes | Number of days the complaint has been open |

### Output
| Field | Type | Description |
|---|---|---|
| category | string | One of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other |
| priority | string | One of: Urgent, Standard, Low |
| reason | string | One sentence citing specific words from the description |
| flag | string | "NEEDS_REVIEW" if ambiguous, otherwise empty string |

### Logic
1. Lowercase the description.
2. Check against category keyword sets (in order):
   - Pothole: pothole, tyre damage, tire damage
   - Flooding: flood, waterlogging, waterlogged, submerged, knee-deep, stranded
   - Streetlight: streetlight, street light, lights out, dark, flickering, sparking
   - Waste: garbage, waste, litter, overflowing bins, dump, rubbish, dead animal
   - Noise: noise, loud music, music past midnight, honking
   - Road Damage: road surface, cracked, sinking, broken, footpath, tiles broken, upturned
   - Heritage Damage: heritage, monument, historical
   - Heat Hazard: heat, temperature, sunstroke
   - Drain Blockage: drain blocked, drain blockage, manhole, manhole cover
   - Other: default when no keywords match
3. Count how many categories matched. If ≥ 2, set flag = "NEEDS_REVIEW".
4. Select the first matching category (priority order as listed above).
5. Check for severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) or days_open > 15 → priority = "Urgent".
6. Otherwise priority = "Standard". Use "Low" only if description is vague/non-actionable and no category keywords match.
7. Build reason sentence citing the matched keywords.

---

## Skill: batch_classify

### Description
Reads a CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV.

### Inputs
| Parameter | Type | Required | Description |
|---|---|---|---|
| input_path | string | yes | Path to input CSV file |
| output_path | string | yes | Path to write results CSV file |

### Output
A CSV file written to output_path with columns: complaint_id, category, priority, reason, flag.

### Logic
1. Open and parse the input CSV file (columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open).
2. For each row, call classify_complaint(description, days_open).
3. Collect results into a list of dictionaries.
4. Write the results list to output_path as CSV with header row.
5. Print summary statistics (total classified, count per category, count urgent).
