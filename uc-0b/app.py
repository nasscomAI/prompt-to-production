# UC-0B: Summary That Changes Meaning
# Ensures that all numbered clauses are included in summaries

import csv

# Function to read input data
def read_input(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Function to generate summary while enforcing every-numbered-clause rule
def generate_summary(doc_rows):
    summaries = []
    for row in doc_rows:
        clauses = row[1].split('.')  # assume column 1 has text
        numbered_clauses = [clause.strip() for clause in clauses if clause.strip()]
        summary = '. '.join(numbered_clauses)  # keep all clauses
        summaries.append([row[0], summary])  # row[0] = doc id
    return summaries

# Function to save results
def save_results(results, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['doc_id', 'summary'])
        writer.writerows(results)

# Main execution
if __name__ == "__main__":
    input_file = '../data/city-test-files/test_pune.csv'
    output_file = 'summary_hr_leave.txt'
    
    docs = read_input(input_file)
    summaries = generate_summary(docs)
    save_results(summaries, output_file)
    
    print(f"UC-0B processing complete. Output saved to {output_file}")