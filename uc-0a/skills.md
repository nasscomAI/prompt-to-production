# Skills

## classify_complaint
Takes one complaint description as input and determines:
- category
- priority
- reason
- flag

The classification is based on keywords in the description and the allowed category list.  
If severity keywords like injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse appear, the priority must be set to Urgent.

## batch_classify
Reads the input CSV file containing complaint descriptions, applies the classify_complaint function to every row, and writes the results (category, priority, reason, flag) into an output CSV file.
