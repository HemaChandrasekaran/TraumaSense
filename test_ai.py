from transformers import pipeline

print("Loading AI model...")

classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)

text = "I am very scared and worried about my family. I don't feel safe."

results = classifier(text)

print("\nAI Results:")
for result in results[0]:
    if result["score"] > 0.05:
        print(result["label"], ":", round(result["score"], 3))