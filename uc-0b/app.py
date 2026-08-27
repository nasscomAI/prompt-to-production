text = open("../data/policy-documents/policy_hr_leave.txt", encoding="utf-8").read()

# Simple summary
summary = text[:300]

with open("summary_hr_leave.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("Summary created ✅")