from retriever import retrieve_context
from rag_agent import answer_question

question = input("Question: ")

contexts = retrieve_context(question)

print("\nRetrieved Context\n")
print("=" * 80)

for i, c in enumerate(contexts, 1):
    print(f"\nContext {i}\n")
    print(c)

print("\n")
print("=" * 80)

answer = answer_question(question, contexts)

print("\nGemini Answer\n")
print("=" * 80)
print(answer)