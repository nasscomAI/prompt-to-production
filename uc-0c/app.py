import csv
import argparse

def calculate_total(file):
    total = 0
    
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                total += float(row['value'])
            except:
                continue
    
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    total = calculate_total(args.input)
    
    with open(args.output,"w") as f:
        f.write(f"Total: {total}")


if __name__ == "__main__":
    main()
