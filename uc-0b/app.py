import argparse

def summarize_policy(input_file,output_file):

    with open(input_file,"r",encoding="utf-8") as f:
        lines=f.readlines()

    summary=[l.strip() for l in lines if l.strip()]

    with open(output_file,"w",encoding="utf-8") as f:
        for line in summary[:10]:
            f.write(line+"\n")

    print("Summary generated")

if __name__=="__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    summarize_policy(args.input,args.output)