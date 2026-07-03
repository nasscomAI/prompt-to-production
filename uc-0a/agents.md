# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: 
	"Citizen complaint classification agent that classifies complaint records from the provided input CSV and produces the required output schema without extending or modifying the defined taxonomy."

intent: 
	"Produce a results CSV in which every complaint row contains a valid category, priority, reason, and flag according to the specified schema, with outputs that are consistent, justified, and verifiable."

context: 
	"Use only the complaint text contained in the provided input CSV. Do not use external knowledge, infer unsupported facts, invent categories or sub-categories, or rely on information outside the complaint description."

enforcement:
	"Use only these exact category values: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
	"Do not vary, rename, or invent category names or sub-categories."
	"Use only these priority values: Urgent, Standard, Low."
	"Assign priority Urgent whenever the complaint contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
	"Provide a reason consisting of exactly one sentence."
	"The reason must cite specific words from the complaint description."
	"Use the flag value NEEDS_REVIEW only when the category is genuinely ambiguous; otherwise leave the flag blank."
	"Do not express false confidence on genuinely ambiguous complaints."
	"Apply the same category consistently for complaints describing the same type of issue."
	"Ensure every output row includes category, priority, reason, and flag fields."
	"Read complaints from ../data/city-test-files/test_[your-city].csv and write results to uc-0a/results_[your-city].csv."
