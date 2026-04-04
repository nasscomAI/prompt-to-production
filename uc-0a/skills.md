# Skills: Complaint Classifier

## classify_complaint
**Description:** Takes a single complaint row consisting of context like description and determines category, priority, reason, and flag.
**Inputs:** `row: dict`
**Outputs:** dictionary with `complaint_id`, `category`, `priority`, `reason`, `flag`
**Rules:** 
1. Use exact Category string from the allowed list: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
2. priority must be Urgent if severity keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse` are found in the description.
3. Cite the exact word for 'reason' field that led to the priority decision.
4. Set flag to 'NEEDS_REVIEW' if the complaint contains ambiguity (e.g. mentions multiple categories).

## batch_classify
**Description:** Reads a batch of complaints from a CSV and runs `classify_complaint` iteratively to produce a result CSV.
**Inputs:** `input_path: str`, `output_path: str`
**Rules:** 
Must gracefully handle nulls or bad rows, write an ERROR in flag, and write all valid results correctly without crashing.
