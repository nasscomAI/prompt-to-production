# UC-0B Policy Summary Generator

input_file = "../data/policy-documents/policy_hr_leave.txt"
output_file = "summary_hr_leave.txt"

def summarize_policy():
    with open(input_file, "r") as file:
        lines = file.readlines()

    summary = []
    for line in lines:
        if line.strip() != "":
            summary.append(line.strip())

    with open(output_file, "w") as file:
        for line in summary:
            file.write(line + "\n")

    print("Summary generated:", output_file)

if __name__ == "__main__":
    summarize_policy()
