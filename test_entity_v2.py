from app.models.entity_extractor_v2 import EntityExtractor

extractor = EntityExtractor()

tests = [

    "Need 4 AUXO smart switches under 3000 for office",

    "Need wifi smart lock",

    "Building a new house",

    "Need 2 cameras",

    "DashGlasses smart light",

    "camera under 10000"

]

for t in tests:

    print("="*70)

    print(t)

    print(extractor.extract(t))
    