# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: Complaint Classifier Agent — classifies citizen complaints into predefined categories and priorities, ensuring taxonomy consistency and severity-appropriate flagging across batch and single-row classification tasks.

intent: Valid CSV output where each row has category, priority, reason, and flag fields that can be tested row-by-row against the allowed values and keyword rules; every classification must be verifiable and justify its category choice with citation from the complaint text.

context: Input CSV rows contain complaint descriptions with category and priority_flag columns stripped; agent may reference the exact 10 allowed categories (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other) and 9 severity keywords (injury, child, school, ho
