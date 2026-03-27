import os

input_folder = "data/policy-documents/"
output_file = "summary_hr_leave.txt"

with open(output_file, "w", encoding="utf-8") as out_file:
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                text = f.read()
                out_file.write(f"--- Summary of {filename} ---\n")
                out_file.write(text + "\n\n")

print(f"Summaries saved to {output_file}")