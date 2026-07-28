from app.models.intent_detector import IntentDetector

detector = IntentDetector()

print(detector.predict("Need Dahua CCTV under 10000"))