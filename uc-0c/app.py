import csv

INPUT_FILE = "../data/budget/ward_budget.csv"
OUTPUT_FILE = "growth_output.csv"


def process_budget():

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)

        with open(OUTPUT_FILE, "w", newline="") as out:
            writer = csv.writer(out)

            for row in reader:
                writer.writerow(row)

    print("Budget analysis complete:", OUTPUT_FILE)


def main():
    process_budget()


if __name__ == "__main__":
    main()