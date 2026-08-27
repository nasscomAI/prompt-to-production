"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import classifier

def main():
    print("=== UC-X: Policy Assistant Interactive CLI ===")
    print("Loading documents and indexing...")
    
    try:
        index = classifier.retrieve_documents()
        print(f"Index loaded with {len(index)} document entries.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    print("\nType your question about HR, IT, or Finance policy (or 'quit' to exit):")
    
    while True:
        try:
            query = input("\n>> ").strip()
            if query.lower() in ('quit', 'exit'):
                print("Exiting. Goodbye!")
                break
                
            if not query:
                continue
                
            answer = classifier.answer_question(query, index)
            print("-" * 50)
            print(answer)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
