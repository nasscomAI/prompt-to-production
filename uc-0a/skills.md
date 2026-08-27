skill: classify_complaint

description: >
  Reads a civic complaint text and returns exactly one category
  and one priority flag based on keywords found in the text.

input: complaint text string

output:
  - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - priority_flag: one of Urgent, Standard, Low

rules:
  - Match keywords to assign category
  - Urgent if text contains: child, hospital, school, injury, urgent
  - Standard if text contains: broken, not working, burst
  - Low for everything else
  - Never leave category or priority empty
  - Use Other if no category keyword matches
