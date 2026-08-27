import os

DATA_FOLDER = "../data/policy-documents"

def read_documents():

    for file in os.listdir(DATA_FOLDER):

        path = os.path.join(DATA_FOLDER, file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        print("\nDocument:", file)
        print(text[:200])


def main():
    read_documents()


if __name__ == "__main__":
    main()