import os

def search_policy(query):

    folder = "../data/policy-documents"

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        with open(path, encoding="utf-8") as f:
            text = f.read().lower()

            if query.lower() in text:
                return f"Answer found in {file}"

    return "No matching policy found"


def main():

    print("Policy Assistant")
    print("Type a question about policies")

    while True:

        query = input("\nAsk a question (or type exit): ")

        if query.lower() == "exit":
            break

        result = search_policy(query)

        print("Result:", result)


if __name__ == "__main__":
    main()