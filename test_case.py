"""Тест регистронезависимости поиска"""

query1 = "СВЕТИЛЬНИК"
query2 = "светильник"
query3 = "Светильник"

product = "Светильник-ночник аккумуляторный"

for q in [query1, query2, query3]:
    query_words = [word for word in q.lower().split() if len(word) >= 3]
    product_lower = product.lower()
    score = sum(1 for word in query_words if word in product_lower)
    print(f"Запрос: '{q}' → найден: {score > 0} (score={score})")
