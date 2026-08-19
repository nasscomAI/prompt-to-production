from transformers import pipeline

qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

context = """Infosys Springboard is a learning platform offering courses in IT, E&C, and more."""
question = "What is Infosys Springboard?"

answer = qa(question= question, context= context)
print("Answer:",answer['answer'])