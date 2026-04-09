import argparse

def validate(data):
    if not data:
        return "Invalid Data"
    return "Valid Data"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input,'r') as f:
        data = f.read()

    result = validate(data)

    with open(args.output,'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()
