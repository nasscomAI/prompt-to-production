import csv

def batch_classify(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)

        with open(output_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)

            for row in reader:
                text = row[0].lower()

                if "leave" in text:
                    category = "HR Policy"
                elif "computer" in text or "internet" in text:
                    category = "IT Policy"
                elif "reimbursement" in text or "expense" in text:
                    category = "Finance Policy"
                else:
                    category = "General"

                writer.writerow([row[0], category])