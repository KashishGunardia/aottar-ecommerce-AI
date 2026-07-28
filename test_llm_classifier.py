from app.models.llm_classifier import LLMClassifier

clf = LLMClassifier()

tests = [
    "bijli ki zarurat hai",
    "ghar mein andhera hai",
    "office security chahiye",
    "hello",
    "track my order"
]

for t in tests:
    print(t)
    print(clf.classify(t))
    print("-" * 50)