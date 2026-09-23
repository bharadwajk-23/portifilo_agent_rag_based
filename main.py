
from Retreival import load_retriever
from Answer_generation import gen_ans


retriver=load_retriever()

while True:
    print("enter exit or stop  to stop")
    query=input("Enter a question : ")

    if query=='exit' or query=='stop':
        break
    answer=gen_ans(retriver,query)
    print("Generated Response: \n")
    print(answer['answer'])
    print(" ----------")