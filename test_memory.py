from app.memory.conversation_memory import ConversationMemory

memory = ConversationMemory()

memory.update({

    "category": "Smart Switch"

})

print(memory.get())

memory.update({

    "budget": 1000

})

print(memory.get())

memory.update({

    "brand": "AUXO"

})

print(memory.get())

memory.clear()

print(memory.get())
