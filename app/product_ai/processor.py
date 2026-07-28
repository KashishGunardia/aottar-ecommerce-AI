class ProductProcessor:

    def __init__(
        self,
        cleaner,
        extractor,
        classifier,
        tag_generator,
        embedding_generator,
        vector_updater,
    ):
        self.cleaner = cleaner
        self.extractor = extractor
        self.classifier = classifier
        self.tag_generator = tag_generator
        self.embedding_generator = embedding_generator
        self.vector_updater = vector_updater

    def process(self, product):

        # 1
        product = self.cleaner.clean(product)

        # 2
        specs = self.extractor.extract(product)

        # 3
        category = self.classifier.classify(product)

        # 4
        tags = self.tag_generator.generate(product, specs)

        # 5
        embedding = self.embedding_generator.generate(product)

        # 6
        self.vector_updater.update(
            product,
            embedding,
            specs,
            tags,
            category,
        )

        return {
            "status": "success",
            "category": category,
            "tags": tags,
            "specifications": specs,
        }