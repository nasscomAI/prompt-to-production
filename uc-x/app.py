# UC-X Ask My Documents

try:
    file_path = "../data/policy-documents/policy_hr_leave.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    print("Document loaded successfully!")
    print("\nSample Output:\n")
    print(data[:300])  # show first 300 chars

except Exception as e:
    print("Error:", e)
