import argparse

def summarize_policy(input_file, output_file):

    with open(input_file,"r",encoding="utf-8") as f:
        text = f.readlines()

    summary = []

    for line in text:
        line=line.strip()

        if line.startswith(("2.3","2.4","2.5","2.6","2.7","3.2","3.4","5.2","5.3","7.2")):
            summary.append(line)

    with open(output_file,"w",encoding="utf-8") as f:
        for s in summary:
            f.write(s+"\n")

    print("Summary generated")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    summarize_policy(args.input,args.output)


if __name__ == "__main__":
    main()