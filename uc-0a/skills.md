- classify_complaint
  description: >
    Take one complaint record as input (description + optional metadata) and return a dict/object with:
    - category: exact one of {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other}
    - priority: Urgent, Standard, or Low (Urgent if severity keywords present)
    - reason: one sentence citing words from input description
    - flag: NEEDS_REVIEW or blank (ambiguity marker)

- batch_classify
  description: >
    Read input CSV `../data/city-test-files/test_[city].csv`, apply classify_complaint to each row,
    write output CSV `uc-0a/results_[city].csv` with columns [category, priority, reason, flag].
    Ensure no category variations and maintain data order.
