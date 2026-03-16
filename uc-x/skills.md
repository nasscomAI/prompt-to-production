skills:
  - name: outlier_detection_iqr
    description: Identifies and filters statistical anomalies in numerical features using the Interquartile Range method.
    input: Numerical feature column (Pandas Series or List).
    output: A filtered dataset and a list of indices representing detected outliers.
    error_handling: If the input data is non-numerical, it returns a TypeError and suggests categorical encoding first.

  - name: missing_value_imputation
    description: Automatically fills missing data points using mean, median, or mode based on the distribution of the feature.
    input: Raw dataset with null values (CSV or DataFrame).
    output: A complete dataset with no null values and a log of which strategy was used for each column.
    error_handling: If a column is 100% empty, the skill drops the column and alerts the user rather than attempting to impute.

  - name: feature_distribution_analysis
    description: Analyzes the skewness and kurtosis of data to determine if a transformation (like Log or Square Root) is needed.
    input: Preprocessed numerical data (DataFrame).
    output: A statistical summary and a recommendation for the best transformation method.
    error_handling: If the sample size is too small for statistical significance (n < 30), it provides a warning about potential bias.