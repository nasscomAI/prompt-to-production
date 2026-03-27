def generate_summary(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    summary = []

    for line in lines:
        line = line.strip()
        
        if line:
            summary.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in summary:
            f.write(line + "\n")

    print("Summary generated!")