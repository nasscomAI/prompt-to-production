# \# UC-0C Skills

# 

# \## load\_dataset

# 

# Reads the budget CSV file, validates the required columns, reports the

# number of rows and the count of null actual\_spend values, and reports

# which rows are null together with their notes/reasons.

# 

# \## compute\_growth

# 

# Takes ward, category, and growth\_type as explicit inputs and returns a

# per-period table for that ward/category combination.

# 

# The output includes:

# \- period

# \- actual\_spend

# \- growth type

# \- formula used

# \- growth result

# \- null reason when applicable

# 

# Null actual\_spend values are flagged and are not used to silently compute

# growth.

