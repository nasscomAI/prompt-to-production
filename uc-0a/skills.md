# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
	description: Classifies a single citizen complaint into the required schema with justification and ambiguity handling.
	input:
		type: object
		format:
			complaint: string
	output:
		type: object
		format:
			category: "One of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
			priority: "One of: Urgent, Standard, Low"
			reason: "Single sentence citing specific words from the complaint description"
			flag: "NEEDS_REVIEW or empty string"
	error_handling:
		invalid_input: "Return NEEDS_REVIEW, set category to Other, priority to Standard, and provide a reason indicating the complaint text is missing or invalid."
		ambiguous_input: "Set flag to NEEDS_REVIEW, avoid false confidence, choose Other if no allowed category is clearly supported, and explain the ambiguity in the reason."
		failure_modes:
			- "Reject taxonomy drift by using only the exact allowed category names."
			- "Assign Urgent whenever severity keywords are present: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
			- "Always include a one-sentence reason citing specific words from the complaint."
			- "Do not invent sub-categories."
  - name: batch_classify
	description: Reads an input CSV of complaints, classifies each row using classify_complaint, and writes the required output CSV.
	input:
		type: CSV file
		format: "CSV with complaint rows where category and priority_flag columns are absent."
	output:
		type: CSV file
		format: "CSV preserving input rows and adding category, priority, reason, and flag columns."
	error_handling:
		invalid_input: "Report invalid or unreadable CSV input and do not produce partial classifications."
		ambiguous_input: "Propagate NEEDS_REVIEW from classify_complaint for ambiguous rows."
		failure_modes:
			- "Ensure all category values exactly match the allowed taxonomy."
			- "Ensure Urgent is assigned when severity keywords are detected."
			- "Include a reason for every classified row."
			- "Never fabricate unsupported categories or classify ambiguous complaints with unwarranted confidence."