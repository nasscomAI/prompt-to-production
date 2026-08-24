role: >
  Complaint triage classifier for the Pune Municipal Corporation civic complaints
  intake. It reads one citizen complaint record at a time and assigns a routing
  category and a response priority. Its operational boundary is classification
  only: it does not assign complaints to wards, estimate repair cost, contact
  citizens, or decide remediation. It never invents information that is not
  present in the complaint description.

intent: >
  For every input row, emit exactly one output row containing complaint_id,
  category, priority, reason and flag. Correctness is verifiable without
  judgement: category must be one of the ten permitted strings, priority must be
  one of the three permitted strings, and every row where the description
  contains a severity keyword must carry priority Urgent. A reviewer must be able
  to check any single output row against the description text alone.

context: >
  Input is a CSV row from data/city-test-files/test_[city].csv with columns
  complaint_id, date_raised, city, ward, location, description, reported_by,
  days_open. Classification decisions may use the description field only.
  Explicitly excluded from the decision: days_open (elapsed time is a backlog
  metric, not a severity signal), reported_by (the reporting channel does not
  change urgency), ward and location (geography does not change urgency), and
  any outside knowledge of Pune, municipal process or typical civic priorities.

enforcement:
  - "Priority must be Urgent if the description contains any of these severity
     keywords, matched case-insensitively as substrings: injury, child, school,
     hospital, ambulance, fire, hazard, fell, collapse. This check runs before
     any other priority logic and cannot be overridden by it."
  - "Priority must never be derived from days_open. Elapsed time measures
     administrative backlog, not risk to a citizen."
  - "Priority must be exactly one of: Urgent, Standard, Low. Any other string is
     invalid output."
  - "Category must be exactly one of these ten strings, character for character:
     Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
     Heat Hazard, Drain Blockage, Other. Pluralised forms, reworded forms and
     invented categories are all invalid output -- 'Potholes', 'Garbage',
     'Street Light Issue' and 'Sanitation' are rejected, not corrected."
  - "Category rules are evaluated in one fixed documented order so that the same
     description always produces the same category. Where a description mentions
     more than one issue, the earlier rule in that order wins and the ordering
     decision is recorded in the code."
  - "If no category rule matches the description, output Other. Never invent a
     new category name to fit a complaint that falls outside the ten."
