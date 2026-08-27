# Skills Definition — Complaint Classifier

## Skill 1: Text Classification
- Read the complaint text
- Identify keywords related to civic issues
- Map keywords to one of: Roads, Water Supply, Sanitation, Electricity, Other

## Skill 2: Severity Assessment
- Scan for emergency keywords: injury, accident, child, school, hospital, flooding, fire
- If found → HIGH
- If complaint affects multiple households or blocks public access → MEDIUM to HIGH
- If minor/cosmetic issue → LOW

## Skill 3: Structured Output
- Always return output as: category, severity
- Format must be consistent so it can be written to a CSV file

## Keyword Reference
| Category      | Keywords                                           |
|---------------|----------------------------------------------------|
| Roads         | road, pothole, footpath, traffic, accident, bridge |
| Water Supply  | water, pipe, leak, tap, supply, drainage           |
| Sanitation    | garbage, waste, dustbin, sweeping, smell, drain    |
| Electricity   | light, streetlight, power, electric, wire, pole    |
| Other         | anything that doesn't fit above                    |
