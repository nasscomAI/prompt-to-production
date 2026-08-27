skills:
  - name: load_dataset
    description: Load dataset from csv file
    input: CSV with columns period, ward, category, budgeted_amount, actual_spend and notes
    output: None
    error_handling: Reports null values with rows and continues processing 

  - name: compute_growth
    description: Computes growth rate based on growth type
    input: CSV file with columns columns period, ward, category, budgeted_amount, actual_spend and notes
    output: Row with ward, category, period, actual spend(inlakh),  growth rate
    error_handling: Reports null values with rows and continues processing 
