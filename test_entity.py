from app.models.entity_extractor import EntityExtractor

extractor = EntityExtractor()

print(

    extractor.extract(

        "Need Dahua CCTV under 10000 for my office"

    )

)