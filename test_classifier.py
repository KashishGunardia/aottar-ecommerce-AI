from app.models.query_classifier import QueryClassifier

classifier = QueryClassifier()

tests = [

    "hello",

    "need smart switch",

    "building a new house",

    "track my order",

    "refund",

    "become vendor",

    "camera under 5000",

    "idiot",

    "tell me a joke",

    "office security"

]

for t in tests:

    print(t)

    print(classifier.classify(t))

    print("-"*40)
    