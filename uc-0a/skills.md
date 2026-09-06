Skill: Pune Municipal Citizen Complaint Classifier Workflow (UC-0A)
Overview
This skill defines the standardized step-by-step procedure for classifying Pune municipal citizen complaints into a single standard category, determining an appropriate priority level, and articulating a concise, evidence-based rationale
Input Requirements
Each incoming record must contain the following attributes:
complaint_id: Unique identifier for the complaint.
description: Detailed text describing the issue reported by the citizen.
days_open: Number of days elapsed since the complaint was raised.
Optional contextual fields: date_raised, city, ward, location, reported_by.
Execution Workflow
Step 1: Read and Validate Complaint Data
Read the input complaint fields carefully.
Ensure critical fields (complaint_id, description, days_open) are non-empty.
Establish a baseline constraint: Do not invent information that is not explicitly present in the input text.
Step 2: Identify the Primary Issue
Analyze the description field to extract key entities, hazards, affected parties, and physical assets involved.
If multiple issues are mentioned in a single complaint, determine which issue represents the root cause or primary impact described by the citizen.
Step 3: Select Category
Map the primary issue to exactly one of the following seven fixed categories:
Category
Typical Issues Included
Roads
Potholes, road surface cracking, sinking asphalt, utility cut damage, road collapse, missing or damaged manhole covers. 
Drainage/Flooding
Flooded underpasses, waterlogging, blocked drains.
Streetlights
Non-functioning streetlights, flickering lights, dark streets, exposed wires/sparking.
Garbage/Waste
Overflowing garbage bins, unauthorized dumping of construction/bulk waste, uncollected trash.
Noise Complaint
Loudspeakers, late-night music, commercial/construction noise in residential areas.
Animal/Waste
Dead animal removal, stray animal hazards, animal waste accumulation.
Footpath
Broken pavement, upturned tiles, footpath encroachments, damaged pedestrian pathways.
Step 4: Evaluate Risk Factors & Criteria
Assess the complaint against the following six decision criteria:
Safety Risk: Immediate physical danger (e.g., electrical sparks, deep exposed holes).
Health & Environmental Risk: Disease vectors, decaying organic matter, foul odor.
Affected Population: Impact on individuals vs. school children, commuters, or whole neighborhoods.
Accessibility & Traffic: Road closures, stranded commuters, blocked underpasses or transit hubs.
Accident / Damage Occurrence: Has an accident, injury, or vehicle damage already occurred?
Days Open: Duration the issue has remained unresolved (e.g., long-standing issues vs. fresh complaints).
Step 5: Assign Priority
Assign exactly one priority level based on the evaluation in Step 4:
High Priority
Assign High Priority if ANY of the following conditions are met:
Immediate or serious safety risk (e.g., electrical hazards, sparking streetlights).
Missing manhole cover or similar high-severity injury risk.
Severe flooding rendering roads, underpasses, or bridges completely inaccessible.
Serious safety risks specifically targeting vulnerable groups (children, cyclists, pedestrians).
Problem has already caused an accident, physical injury, or vehicle/property damage.
Medium Priority
Assign Medium Priority if the issue does NOT meet High Priority criteria, but meets ANY of the following:
Significant public inconvenience or health/environmental concern (e.g., decaying animals, overflowing market garbage).
Problems affecting a large number of people without immediate life-threatening safety risk.
Complaints remaining unresolved for a considerable number of days (e.g., > 7-10 days open).
Repeated or persistent public-service outages (e.g., multiple streetlights out across a main avenue).
Low Priority
Assign Low Priority if:
The issue represents a minor localized inconvenience.
Limited impact with no significant safety, health, or accessibility risks.
Very recent minor issue with low risk.
Step 6: Formulate Short Evidence-Based Reason
Write a brief single-sentence explanation (10–20 words).
Explicitly cite the key facts from the description that drove the priority assignment (e.g., actual damage reported, duration open, specific electrical hazard, vulnerable group affected).
Do not introduce external assumptions or unmentioned facts.
Step 7: Validate and Output
Verify that:
Category is one of the 7 official categories.
Priority is strictly High Priority, Medium Priority, or Low Priority.
Reason directly matches the criteria used.
Format the result using the strict pipe-delimited format:
Complaint ID | Category | Priority | Reason
Worked Example Reference
Complaint ID
Description Excerpt
Category
Priority
Key Decision Factor
PM-202401
Pothole damaged 3 vehicles
Roads
High Priority
Vehicle damage already occurred
PM-202411
Streetlight flickering and sparking
Streetlights
High Priority
Immediate electrical hazard
PM-202413
Overflowing garbage near market, open 13 days
Garbage/Waste
Medium Priority
Health concern open > 10 days
PM-202418
Wedding venue playing music past midnight
Noise Complaint
Low Priority
Minor residential inconvenience
