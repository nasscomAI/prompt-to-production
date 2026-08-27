import argparse

def generate_summary(input_path, output_path):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        summary = []

        for line in lines:
            line = line.strip()
            if line:
                summary.append(line)

        with open(output_path, "w", encoding="utf-8") as f:
            for line in summary:
                f.write(line + "\n")

        print("Summary generated ✅")

    except Exception as e:
        print("Error:", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    generate_summary(args.input, args.output)


if __name__ == "__main__":
    main()