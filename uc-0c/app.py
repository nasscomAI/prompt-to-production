import argparse
import csv

def main():

    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r") as infile:
        reader = csv.DictReader(infile)

        with open(args.output, "w", newline="") as outfile:
            fieldnames = reader.fieldnames + ["growth"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                try:
                    prev = float(row["previous_budget"])
                    curr = float(row["current_budget"])

                    growth = curr - prev
                    row["growth"] = growth

                    writer.writerow(row)

                except:
                    row["growth"] = "error"
                    writer.writerow(row)

    print("Growth calculation completed")


if __name__ == "__main__":
    main()