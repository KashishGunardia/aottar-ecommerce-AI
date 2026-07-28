from app.ranking.product_ranker import ProductRanker

ranker = ProductRanker()

entities = {

    "brand": "auxo",

    "category": "smart switch",

    "budget": 2000,

    "feature": ["smart"]

}

products = [

    {

        "name":"AUXO Smart Switch",

        "brand":"auxo",

        "category":"smart switch",

        "price":"1500"

    },

    {

        "name":"Smart Lock",

        "brand":"aottor",

        "category":"smart lock",

        "price":"1800"

    },

    {

        "name":"Premium Switch",

        "brand":"auxo",

        "category":"switch",

        "price":"2500"

    }

]

print(ranker.rank(products, entities))