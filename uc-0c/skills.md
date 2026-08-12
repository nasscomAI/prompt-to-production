
skills:
  - name: [load_dataset]
    description: [Read the supplied ward budget CSV, validate the required columns,
      identify every null actual_spend value, and report the affected rows
      together with the corresponding reason from the notes column.]
    input: [A ward budget CSV file containing period, ward, category,
      budgeted_amount, actual_spend, and notes.
]
    output: [ A validated dataset with the null count and every null row identified,
      including its period, ward, category, and notes reason.]
    error_handling: [If required columns are missing or the dataset cannot be read,
      stop and report the validation error instead of producing a result.]

  - name: [compute_growth]
    description: [Calculate growth for the explicitly requested ward and category at
      per-period level using the explicitly requested growth type. Show the
      formula used alongside every computed result and never silently choose
      a growth method.]
    input: [A validated dataset, one ward, one category, and an explicitly
      specified growth type such as MoM.]
    output: [A per-period table containing the ward, category, period, actual spend,
      growth type, formula, growth result, and any applicable null flag
      and null reason.]
    error_handling: [Refuse to calculate if the growth type is missing, the request asks
      for aggregation across all wards or categories, or a required current
      or previous actual_spend value is null. Report the null reason from
      the notes column instead of computing growth.]
    
