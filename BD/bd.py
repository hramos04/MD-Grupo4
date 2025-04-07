from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")

db = client['projeto_md']
users_collection = db['users']

user_doc = {
    "_username": "Hugo Ramos",
    "conversations": [
        {
            "messages": [
                {"role": "user", "text": "Quantas horas de sono são necessárias?"},
                {"role": "bot", "text": "A quantidade ideal de sono varia, mas geralmente recomenda-se entre 7 a 9 horas por noite."},
            ],
            "thumbnail": "https://example.com/thumb.jpg",
            "created_at": datetime.now()
        }
    ],
    "user_info": {
        "idade": 21,
        "preferencias": ["sono", "alimentação", "desporto"]
    }
}

users_collection.insert_one(user_doc)

print("Utilizador inserido com sucesso")