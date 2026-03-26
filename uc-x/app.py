def find_matches(query, docs):
    matches = {}

    # remove common useless words
    stopwords = {"can", "i", "the", "is", "a", "an", "for", "to", "of", "my"}

    keywords = [
        word.lower() for word in query.split()
        if word.lower() not in stopwords
    ]

    for name, content in docs.items():
        lines = content.split("\n")

        for line in lines:
            line_lower = line.lower()

            # check if multiple keywords match
            match_count = sum(1 for word in keywords if word in line_lower)

            if match_count >= 2:   # require stronger match
                if name not in matches:
                    matches[name] = []
                matches[name].append(line)

    return matches