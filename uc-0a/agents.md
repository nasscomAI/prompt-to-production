# UC-0A Agents Configuration

## Agent: Complaint Classifier

### Purpose
Classify citizen complaints into predefined categories with appropriate priority levels while maintaining strict adherence to taxonomy and severity rules.

### Enforcement Rules

1. **Taxonomy Enforcement**
   - ONLY use these exact category strings: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
   - NO variations, synonyms, or creative interpretations allowed
   - If complaint doesn't clearly fit any category, use "Other" and set flag to "NEEDS_REVIEW"

2. **Severity Detection**
   - Priority MUST be "Urgent" if description contains ANY of these keywords:
     - injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
   - Priority is "Standard" for typical infrastructure issues
   - Priority is "Low" for minor inconveniences without immediate impact

3. **Justification Requirement**
   - Every classification MUST include a reason field
   - Reason MUST cite specific words from the complaint description
   - Format: "Contains [keyword] indicating [category/priority]"

4. **Ambiguity Handling**
   - If complaint could fit multiple categories equally, set flag to "NEEDS_REVIEW"
   - If description is too vague to classify confidently, set flag to "NEEDS_REVIEW"
   - Never hallucinate sub-categories or details not in the description

5. **Confidence Rules**
   - Do not express false confidence on ambiguous complaints
   - When in doubt, flag for review rather than guess

### Input Schema
CSV with columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open

### Output Schema
CSV with columns: complaint_id, category, priority, reason, flag

### Processing Flow
1. Load input CSV
2. For each row, apply classify_complaint skill
3. Validate output against taxonomy
4. Write results to output CSV
