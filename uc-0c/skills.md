# \# Skills

# 

# \## load\_dataset

# Reads the ward budget CSV dataset.

# 

# Responsibilities:

# \- Load the CSV file.

# \- Validate required columns (ward, category, period, spend, notes).

# \- Count and report NULL values before computation.

# \- Return the cleaned dataset for analysis.

# 

# 

# \## compute\_growth

# Computes growth values for a specific ward and category.

# 

# Rules:

# \- Growth type must be specified (MoM or YoY).

# \- Never aggregate across wards or categories.

# \- If spend value is NULL, flag the row instead of computing.

# \- Output must include the formula used for the growth calculation.

# 

# Output:

# Ward, Category, Period, Spend, Growth, Formula

