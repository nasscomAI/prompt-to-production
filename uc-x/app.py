print("UC-X running")

text = "leave policy allows 12 days casual leave per year"

query = "leave"

if query in text:
    result = "Answer found in document"
else:
    result = "Not found"

with open("output.txt", "w") as f:
    f.write(result)

print(result)
