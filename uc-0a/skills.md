# UC-0A Classifier Skills

## classify_complaint
**Input**: Text description of a complaint.
**Logic**:
1. **Category Selection**: Map the description to exactly one of: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
2. **Priority Check**: 
   - Scan for: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`.
   - If found → `Urgent`.
   - Else if description implies safety risk → `Standard`.
   - Else → `Low`.
3. **Reason Generation**: Construct a sentence like: "Classified as [Category] because the text mentions '[keyword]'."
4. **Flagging**: If text matches multiple categories or is nonsensical → `NEEDS_REVIEW`.

## batch_classify
**Input**: Path to a CSV file containing `complaint_id` and `description`.
**Logic**:
1. Read the input CSV.
2. Initialize an output CSV with columns: `complaint_id`, `description`, `category`, `priority`, `reason`, `flag`.
3. For each row, execute `classify_complaint`.
4. Save results to the specified output path.
