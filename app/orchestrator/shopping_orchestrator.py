from app.recommendation.recommendation_engine import RecommendationEngine
from app.comparison.comparison_engine import ComparisonEngine
from app.inventory.inventory_engine import InventoryEngine
from app.upsell.upsell_engine import UpsellEngine
from app.knowledge.knowledge_engine import KnowledgeEngine


class ShoppingOrchestrator:

    def __init__(self):

        self.recommendation = RecommendationEngine()
        self.comparison = ComparisonEngine()
        self.inventory = InventoryEngine()
        self.upsell = UpsellEngine()
        self.knowledge = KnowledgeEngine()