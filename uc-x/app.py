import os
import re

class PolicyAgent:
    def __init__(self):
        self.policy_files = [
            "policy_hr_leave.txt",
            "policy_it_acceptable_use.txt",
            "policy_finance_reimbursement.txt"
        ]
        self.data_dir = os.path.join("..", "data", "policy-documents")
        self.index = []
        self.refusal_template = (
            "This question is not covered in the available policy documents\n"
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
            "Please contact [relevant team] for guidance."
        )

    def retrieve_documents(self):
        """
        Loads and indexes the policy files by document name and section number.
        """
        for filename in self.policy_files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                # Fallback to local data dir if running from different context
                filepath = os.path.join("data", "policy-documents", filename)
                if not os.path.exists(filepath):
                    # One more try for common workspace layout
                    filepath = os.path.join("..", "prompt-to-production", "data", "policy-documents", filename)
                    if not os.path.exists(filepath):
                        print(f"Warning: {filename} not found at expected paths.")
                        continue

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self._parse_content(filename, content)

    def _parse_content(self, filename, content):
        """
        Parses content into sections based on N. and N.M numbering.
        """
        # Split by section headers (digit followed by dot and space)
        # We look for lines like "2. ANNUAL LEAVE"
        sections = re.split(r'\n\s*════+.*\n', content)
        
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
                
            # Find sub-points like 2.1, 2.2, etc.
            # Using a regex that captures the number and the following text until the next number
            matches = re.finditer(r'(\d+\.\d+)\s+(.*?)(?=\d+\.\d+\s+|$)', sec, re.DOTALL)
            
            for match in matches:
                num = match.group(1)
                text = match.group(2).strip()
                # Clean up multiple spaces and newlines
                text = re.sub(r'\s+', ' ', text)
                self.index.append({
                    "source": filename,
                    "section": num,
                    "content": text,
                    "full_text": text.lower()
                })

    def answer_question(self, query):
        """
        Searches the index for the best matching single-source answer.
        """
        if not query.strip():
            return "Please provide a question."

        query_lower = query.lower()
        # Extract keywords (min 3 chars)
        query_tokens = set(re.findall(r'\b\w{3,}\b', query_lower))
        
        # Explicitly required keywords for some queries
        if "leave" in query_lower and "carry" in query_lower:
            query_tokens.add("carry")
            query_tokens.add("forward")

        if not query_tokens:
            return self.refusal_template

        results = []
        for entry in self.index:
            entry_text = entry["full_text"]
            score = 0
            for token in query_tokens:
                if token in entry_text:
                    score += 1
            
            if score > 0:
                results.append((score, entry))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)

        if not results or results[0][0] < 1: 
            return self.refusal_template

        # Check for blending/ambiguity
        top_score = results[0][0]
        top_matches = [r for r in results if r[0] == top_score]
        
        # Group by source to ensure single-source
        unique_sources = {m[1]["source"] for m in top_matches}
        
        if len(unique_sources) > 1:
            # Check if one source is significantly better (not implemented here for simplicity)
            # If genuinely ambiguous, refuse
            return self.refusal_template

        # Pick the best match
        best_match = top_matches[0][1]
        
        # Cite source document name + section number
        response = f"{best_match['content']}\n\n[Source: {best_match['source']} | Section: {best_match['section']}]"
        return response

def main():
    print("--- Policy Support Agent (UC-X) ---")
    print("Indexing documents...")
    
    agent = PolicyAgent()
    try:
        agent.retrieve_documents()
        if not agent.index:
            print("Warning: Index is empty. Check document formatting and paths.")
        else:
            print(f"Indexed {len(agent.index)} policy sections.")
        print("Ready. Ask me about HR, IT, or Finance policies.\n")
    except Exception as e:
        print(f"Error initializing: {e}")
        return

    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
            
            if not query:
                continue

            answer = agent.answer_question(query)
            print(f"\nAgent: {answer}\n")
            print("-" * 40)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
