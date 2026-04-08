"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import json

def retrieve_policy(file_path):
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found."}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.readlines()
        except Exception as e:
            return {"error": f"Failed to read file with fallback encoding: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}
    
    # Combine lines belonging to the same clause
    combined_lines = []
    temp_line = ""
    for line in content:
        if line.strip():
            if line[0].isdigit() and (line[1] == '.' or line[2] == '.'):  # New clause starts
                if temp_line:
                    combined_lines.append(temp_line.strip())
                temp_line = line.strip()
            else:
                temp_line += " " + line.strip()
    if temp_line:
        combined_lines.append(temp_line.strip())

    # Process combined lines into structured data
    structured_data = {}
    for line in combined_lines:
        parts = line.split(' ', 1)
        if len(parts) == 2 and parts[0].replace('.', '').isdigit():
            structured_data[parts[0]] = parts[1].strip()
            
    return structured_data

def summarize_policy(structured_data):
    """
    Produces a compliant tabular summary of policy documents with clause references.
    """
    if "error" in structured_data:
        return {"error": structured_data["error"]}
    try:
        summary = []
        for clause, content in structured_data.items():
            if not content:
                return {"error": f"Clause {clause} is missing content."}

            # Extract core obligation and binding verb
            # Ensure multi-condition obligations are preserved
            else:
                core_obligation = content.split('.', 1)[0].strip() + '.'  # Extract the first full sentence ending with a period
                binding_verb = ""
                for verb in ["must", "will", "may", "requires", "not permitted", "cannot"]:
                    if verb in content:
                        binding_verb = verb
                        break

            summary.append({"Clause": clause, "Core obligation": core_obligation, "Binding verb": binding_verb})

        # Format as tabular output
        output = "| Clause | Core obligation | Binding verb |\n"
        output += "|---|---|---|\n"
        for row in summary:
            output += f"| {row['Clause']} | {row['Core obligation']} | {row['Binding verb']} |\n"
        return output
    except Exception as e:
        return {"error": f"Failed to summarize policy: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization Tool")
    parser.add_argument("--input", required=True, help="Path to the input .txt policy file")
    parser.add_argument("--output", required=True, help="Path to the output summary file")
    args = parser.parse_args()

    # Step 1: Retrieve policy
    policy_data = retrieve_policy(args.input)
    if "error" in policy_data:
        print(f"Error: {policy_data['error']}")
        return

    # Step 2: Summarize policy
    summary = summarize_policy(policy_data)
    if "error" in summary:
        print(f"Error: {summary['error']}")
        return

    # Step 3: Write summary to output file
    try:
        with open(args.output, 'w', encoding='utf-8') as output_file:
            output_file.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: Failed to write summary to file: {str(e)}")

if __name__ == "__main__":
    main()
