import csv

def show_complaints():

    file = "../data/city-test-files/test_hyderabad.csv"

    with open(file, encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            print(row["complaint_id"], "-", row["description"])


def main():

    print("City Complaint Viewer\n")

    show_complaints()


if __name__ == "__main__":
    main()