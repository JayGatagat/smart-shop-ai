import re

PRODUCTS = [
 {"id":1,"name":"Wireless Headphones","category":"Electronics","price":2499,"rating":4.5,"emoji":"🎧","image":"https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80","badge":"Best Seller","description":"Wireless Bluetooth audio for music and calls.","tags":"audio music bluetooth headphones","stock":18},
 {"id":2,"name":"Smart Watch","category":"Electronics","price":3299,"rating":4.2,"emoji":"⌚","image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80","badge":"New","description":"Activity tracking and everyday notifications.","tags":"watch fitness steps wearable","stock":12},
 {"id":3,"name":"USB-C Fast Charger","category":"Electronics","price":799,"rating":4.4,"emoji":"🔌","image":"https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=80","badge":"Popular","description":"Compact charger for compatible phones.","tags":"charger phone usb charging","stock":35},
 {"id":4,"name":"Everyday Backpack","category":"Lifestyle","price":1199,"rating":4.3,"emoji":"🎒","image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80","badge":"Campus Pick","description":"Lightweight bag for college and travel.","tags":"bag travel college backpack","stock":20},
 {"id":5,"name":"Insulated Water Bottle","category":"Lifestyle","price":499,"rating":4.6,"emoji":"🧴","image":"https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80","badge":"Eco","description":"Reusable bottle for work, college and fitness.","tags":"bottle water fitness reusable","stock":42},
 {"id":6,"name":"Desk Lamp","category":"Home","price":899,"rating":4.1,"emoji":"💡","image":"https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80","badge":"Study Essential","description":"Adjustable LED lamp for study and work.","tags":"lamp study light desk","stock":16},
 {"id":7,"name":"Mechanical Keyboard","category":"Electronics","price":2799,"rating":4.7,"emoji":"⌨️","image":"https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=900&q=80","badge":"Top Rated","description":"Tactile keys for typing and gaming.","tags":"keyboard gaming typing computer","stock":9},
 {"id":8,"name":"Ceramic Coffee Mug","category":"Home","price":349,"rating":4.0,"emoji":"☕","image":"https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80","badge":"Home Favorite","description":"Ceramic mug for coffee and tea.","tags":"mug coffee tea kitchen","stock":30},
 {"id":9,"name":"Running Shoes","category":"Lifestyle","price":2199,"rating":4.4,"emoji":"👟","image":"https://images.unsplash.com/photo-1543508282-6319a3e2621f?auto=format&fit=crop&w=900&q=80","badge":"Athlete Pick","description":"Everyday shoes for walking and jogging.","tags":"shoes running fitness sports","stock":14},
]
CATEGORIES = ["All", "Electronics", "Lifestyle", "Home"]

SYNONYMS = {
    "earphones": "headphones",
    "headset": "headphones",
    "phones": "phone",
    "charger": "charger",
    "keyboard": "keyboard",
    "laptop": "computer",
    "college": "college",
    "study": "study",
    "fitness": "fitness",
    "gym": "fitness",
    "travel": "travel",
    "bag": "backpack",
    "bottle": "water bottle",
    "water": "water bottle",
    "music": "audio",
    "gaming": "gaming",
    "coffee": "coffee",
    "tea": "coffee",
    "work": "desk",
}

KEYWORD_HINTS = {
    "study": ["desk", "lamp", "keyboard", "study", "backpack", "chair"],
    "college": ["backpack", "bottle", "study", "desk", "lamp"],
    "fitness": ["fitness", "watch", "shoes", "bottle", "water"],
    "music": ["headphones", "audio", "bluetooth"],
    "gaming": ["gaming", "keyboard", "headphones", "computer"],
    "travel": ["backpack", "bottle", "travel"],
    "coffee": ["coffee", "mug", "tea"],
    "phone": ["phone", "charger"],
}


def get_product(pid):
    return next((p for p in PRODUCTS if p["id"] == pid), None)


def recommend(products, query="", category="All", sort="featured"):
    results = [p for p in products if category == "All" or p["category"] == category]
    terms = re.findall(r"[a-z0-9]+", query.lower())
    if terms:
        expanded = set()
        for term in terms:
            expanded.add(term)
            expanded.add(SYNONYMS.get(term, term))
        results = [
            p for p in results
            if any(t in (p["name"] + " " + p["category"] + " " + p["description"] + " " + p["tags"]).lower() for t in expanded)
        ]
    if sort == "price_low":
        results.sort(key=lambda p: p["price"])
    elif sort == "price_high":
        results.sort(key=lambda p: -p["price"])
    elif sort == "rating":
        results.sort(key=lambda p: -p["rating"])
    else:
        results.sort(key=lambda p: (-p["rating"], p["price"]))
    return results


def _extract_budget(question):
    match = re.search(r"(?:under|below|within|less than|upto|up to|max|maximum)\s*(?:₹|rs\.?\s*)?(\d[\d,]*)", question.lower())
    if not match:
        match = re.search(r"(?:₹|rs\.?\s*)(\d[\d,]*)", question.lower())
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def assistant_reply(question, products):
    q = (question or "").lower().strip()
    if not q:
        return "Tell me what you need and your budget, for example: suggest study products under ₹1500."

    budget = _extract_budget(q)
    search_terms = set(re.findall(r"[a-z]+", q))
    expanded_terms = set()
    for term in search_terms:
        expanded_terms.add(term)
        if term in SYNONYMS:
            expanded_terms.add(SYNONYMS[term])

    if not expanded_terms:
        expanded_terms = {"study", "fitness", "music", "travel", "phone"}

    matched = set()
    for keyword, hints in KEYWORD_HINTS.items():
        if keyword in expanded_terms or any(hint in expanded_terms for hint in hints):
            matched.update(hints)

    candidates = []
    for p in products:
        hay = (p["name"] + " " + p["description"] + " " + p["tags"]).lower()
        if budget is not None and p["price"] > budget:
            continue

        score = 0
        for term in expanded_terms:
            if len(term) > 2 and term in hay:
                score += 2
        for term in matched:
            if len(term) > 2 and term in hay:
                score += 1

        if score or not expanded_terms:
            candidates.append((score, p))

    if not candidates:
        visible = [p for p in products if budget is None or p["price"] <= budget]
        if not visible:
            return "No demo products found within that budget. Try a higher budget."
        candidates = [(0, p) for p in sorted(visible, key=lambda p: (-p["rating"], p["price"]))[:3]]

    candidates.sort(key=lambda x: (-x[0], -x[1]["rating"], x[1]["price"]))
    top = candidates[:3]

    lines = ["Here are some suggestions from the demo catalog:"]
    for _, p in top:
        lines.append(f"• {p['name']} — ₹{p['price']:,} (rating {p['rating']}/5): {p['description']}")

    lines.append("\nNote: This is a local keyword-and-budget recommender, not a trained AI model or live product feed.")
    return "\n".join(lines)
