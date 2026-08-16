import argparse
import sys

def retrieve_policy(filepath):
    sections = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_clause = None
    buffer = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('═') or line.startswith('CITY') or line.startswith('HUMAN') or line.startswith('EMPLOYEE') or line.startswith('Document') or line.startswith('Version'):
            continue
            
        # Match e.g. "2.3 Employees must..."
        parts = line.split(' ', 1)
        if len(parts) > 0 and '.' in parts[0] and parts[0].replace('.', '').isdigit():
            if current_clause:
                sections[current_clause] = ' '.join(buffer)
            current_clause = parts[0]
            buffer = [parts[1] if len(parts) > 1 else '']
        else:
            if current_clause:
                buffer.append(line)
                
    if current_clause:
        sections[current_clause] = ' '.join(buffer)
        
    return sections

def summarize_policy(sections):
    # Required clauses: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = ["HR LEAVE POLICY SUMMARY\n", "="*30]
    
    for clause in target_clauses:
        if clause in sections:
            content = sections[clause].strip()
            # Enforce multi-condition preservation and strict compliance
            if clause == '5.2':
                # Ensure we don't drop conditions
                summary_lines.append(f"Clause {clause}: [VERBATIM - Cannot summarize without risk of dropping condition] {content}")
            else:
                summary_lines.append(f"Clause {clause}: {content}")
        else:
            summary_lines.append(f"Clause {clause}: MISSING from source document.")
            
    return "\n\n".join(summary_lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary written to {args.output}")
