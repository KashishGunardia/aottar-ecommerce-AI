from app.pipelines.shopping_pipeline import ShoppingPipeline

pipeline = ShoppingPipeline()

result = pipeline.process(
    "Need Dahua CCTV under 10000 for my office"
)

print(result["reply"])

print(result["products"])