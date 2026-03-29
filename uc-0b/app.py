# UC-0B Summary Generator

input_file = "../data/policy-documents/policy_hr_leave.txt"
output_file = "summary_hr_leave.txt"

try:
    with open(input_file, "r", encoding="utf-8") as f:
        data = f.read()

    # Simple safe summary (no data loss)
    lines = data.split("\n")
    summary = "\n".join(lines[:10])  # first 10 lines

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary created successfully!")

except Exception as e:
    print("Error:", e)
