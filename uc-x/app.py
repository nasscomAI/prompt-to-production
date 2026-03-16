import csv

def count_complaints():

    file = "../data/city-test-files/test_pune.csv"

    total = 0

    with open(file, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            total += 1

    print("Total complaints in file:", total)


def main():

    print("UC-0X Complaint Counter\n")

    count_complaints()


if __name__ == "__main__":
    main()