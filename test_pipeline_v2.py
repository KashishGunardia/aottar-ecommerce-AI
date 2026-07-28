from app.pipelines.shopping_pipeline import ShoppingPipeline

pipe = ShoppingPipeline()

result = pipe.run(
    "Need 4 AUXO smart switches under 3000 for office"
)

for product in result:

    print(product)