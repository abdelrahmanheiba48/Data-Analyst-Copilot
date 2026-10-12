import matplotlib.pyplot as plt
import pipeline

question = input("Ask your data question: ")
r = pipeline.answer(question)

print("\n===== PLAN =====\n")
print(r["plan"])

print("\n===== CODE =====\n")
print(r["code"])

print("\n===== RESULT =====\n")
print(r["output"])

if r["error"]:
    print("ERROR:", r["error"])

if r["figures"]:
    plt.show()
