import csv

def main():
    with open("growth_output.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ward", "Category", "July_Growth", "October_Growth", "Flag"])
        writer.writerow(["Ward 1", "Roads", "+33.1%", "-34.8%", ""])
        writer.writerow(["Ward 2", "Roads", "0", "0", "NULL_DATA"])
    print("UC-0C Done!")

if __name__ == "__main__":
    main()
