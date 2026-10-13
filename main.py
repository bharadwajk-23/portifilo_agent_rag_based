from retrieval import load_retriever
from answer_generation import gen_ans

retriever = load_retriever()

chat_history = []
while True:
    print("enter exit or stop to stop")
    query = input("Enter a question : ")

    if query in ('exit', 'stop'):
        break

    answer = gen_ans(retriever, query, chat_history[-5:])

    print("Generated Response: \n")
    print(answer['answer'])
    chat_history.append(f"Question:{query}-Answer:{answer['answer']}")

    print(" ----------")
