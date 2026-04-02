# Read document
doc = open("../data/policy-documents/policy_hr_leave.txt", encoding="utf-8").read()

# Simple question
question = "leave policy"

# Basic search logic
if question.lower() in doc.lower():
    print("Answer found in document ✅")
else:
    print("Answer not found ❌")