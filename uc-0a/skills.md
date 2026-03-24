# Skills: Complaint Classifier

## classify_complaint
- Input: complaint_text (string)
- Output: category (string), severity (string)
- Logic: Match keywords to determine category and severity level.

### Category Keywords
- Roads: pothole, road, footpath, pavement, traffic, signal, divider
- Water: water, pipe, leak, supply, drainage, drain, flood
- Sanitation: garbage, waste, sewage, toilet, sweeping, dustbin, smell
- Electricity: light, electricity, wire, transformer, power, streetlight
- Parks: park, garden, tree, bench, playground, grass
- Other: anything not matching above

### Severity Keywords (High priority)
- injury, accident, child, school, hospital, fire, danger, emergency, flood, dead

## run_on_csv
- Input: CSV file path with column `complaint_text`
- Output: CSV file with added columns `category` and `severity`
