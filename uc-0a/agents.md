# agents.md

agents:
  - name: complaint_classifier_agent
    objective: Classify civic complaints using the exact UC-0A schema with strict guardrails.
    input: "Complaint row text from ../data/city-test-files/test_[your-city].csv"
    output: "category, priority, reason, flag"
    rules:
      - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
      - "priority must be exactly one of: Urgent, Standard, Low"
      - "If description contains any severity keyword, set priority=Urgent: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
      - "reason must be one sentence and cite specific words from the complaint description"
      - "flag must be NEEDS_REVIEW only when category is genuinely ambiguous; otherwise blank"
    guardrails:
      - "No taxonomy drift: never output category variants or synonyms"
      - "No hallucinated sub-categories"
      - "No missing reason field"
      - "No false confidence on ambiguous descriptions"
      - "No severity blindness on keyword-triggered urgent cases"
