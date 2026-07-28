from langdetect import detect


class LanguageDetector:

    def __init__(self):

        self.rules = {

            # -------------------------
            # English
            # -------------------------

            "hello": "en",
            "hi": "en",
            "hey": "en",
            "good morning": "en",
            "good evening": "en",

            # -------------------------
            # Hinglish (Roman Hindi)
            # -------------------------

            "namaste": "hinglish",
            "namaskar": "hinglish",
            "bhai": "hinglish",
            "bhaiya": "hinglish",
            "mujhe": "hinglish",
            "mera": "hinglish",
            "meri": "hinglish",
            "mere": "hinglish",
            "aap": "hinglish",
            "aapka": "hinglish",
            "aapki": "hinglish",
            "ghar": "hinglish",
            "camera": "hinglish",
            "cctv": "hinglish",
            "lock": "hinglish",
            "switch": "hinglish",
            "light": "hinglish",
            "bijli": "hinglish",
            "problem": "hinglish",
            "chahiye": "hinglish",
            "dikhao": "hinglish",
            "batao": "hinglish",
            "kaise": "hinglish",
            "kitna": "hinglish",
            "price": "hinglish",

            # -------------------------
            # Hindi
            # -------------------------

            "नमस्ते": "hi",
            "नमस्कार": "hi",
            "धन्यवाद": "hi",
            "घर": "hi",
            "अंधेरा": "hi",
            "बिजली": "hi",

            # -------------------------
            # Marathi
            # -------------------------

            "नमस्कार मंडळी": "mr",
            "माझ्या": "mr",
            "मला": "mr",
            "घरात": "mr",
            "लाईट": "mr",
            "दिवा": "mr",

            # -------------------------
            # Gujarati
            # -------------------------

            "નમસ્તે": "gu",
            "જય શ્રી કૃષ્ણ": "gu",
            "ઘર": "gu",

            # -------------------------
            # Punjabi
            # -------------------------

            "ਸਤ ਸ੍ਰੀ ਅਕਾਲ": "pa",

            # -------------------------
            # Bengali
            # -------------------------

            "নমস্কার": "bn",

            # -------------------------
            # Tamil
            # -------------------------

            "வணக்கம்": "ta",

            # -------------------------
            # Telugu
            # -------------------------

            "నమస్కారం": "te",

            # -------------------------
            # Kannada
            # -------------------------

            "ನಮಸ್ಕಾರ": "kn",

            # -------------------------
            # Malayalam
            # -------------------------

            "നമസ്കാരം": "ml"
        }


    def detect(self, text):

        text = text.lower().strip()


        # Rule-based detection
        for keyword, language in self.rules.items():

            if keyword.lower() in text:
                return language


        # Fallback
        try:

            language = detect(text)

            # If langdetect says English but the sentence
            # contains common Hindi words in Roman script,
            # treat it as Hinglish.

            if language == "en":

                hinglish_words = [
                    "hai",
                    "ka",
                    "ki",
                    "ke",
                    "mera",
                    "meri",
                    "mujhe",
                    "aap",
                    "bhai",
                    "chahiye",
                    "dikhao",
                    "batao",
                    "kitna",
                    "kya",
                    "ghar",
                    "camera",
                    "cctv",
                    "switch",
                    "light",
                    "bijli"
                ]

                if any(word in text for word in hinglish_words):
                    return "hinglish"

            return language

        except Exception:
            return "en"