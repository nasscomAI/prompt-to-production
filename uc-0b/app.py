"""
UC-0B — Policy Q&A
"""

import os

def load_policies(folder):
    policies = {}

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), encoding="utf-8") as f:
                policies[file] = f.read()

    return policies


def search_policy(policies, query):
    for name, text in policies.items():
        if query.lower() in text.lower():
            return name, text

    return None


def main():
    policies = load_policies("data/policy-documents")

    query = input("Ask policy question: ")

    result = search_policy(policies, query)

    if result:
        print(result[1])
    else:
        print("No matching policy found")


if __name__ == "__main__":
    main()
