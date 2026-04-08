# UC-X Ask My Documents

file_path = "../data/policy-documents/policy_it_acceptable_use.txt"

# read the document
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

print("Ask a question about the IT policy.")
question = input("Question: ").lower()

# simple keyword search
lines = text.split("\n")

found = False
for line in lines:
    if any(word in line.lower() for word in question.split()):
        print("Answer:", line)
        found = True
        break

if not found:
    print("Answer not found in document.")
