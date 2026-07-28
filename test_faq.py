from app.services.faq_service import FAQService

faq = FAQService()

print(faq.search("What is Aottar?"))
print(faq.search("Do you provide installation?"))
print(faq.search("What is your return policy?"))
print(faq.search("How can I contact you?"))