# UC-0B Policy Summary

input_file = "../data/policy-documents/policy_hr_leave.txt"
output_file = "summary_hr_leave.txt"

# read policy file
with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

# simple summary (first 5 lines)
lines = text.split("\n")
summary = "\n".join(lines[:5])

# save summary
with open(output_file, "w", encoding="utf-8") as f:
    f.write(summary)

print("Summary created in summary_hr_leave.txt")