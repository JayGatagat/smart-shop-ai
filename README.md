# Smart Shop AI

A local demo shopping website built with Python, Flask, HTML and CSS.

## Features
- Demo product catalog with category, price, rating and stock.
- Search, category filters and sorting.
- Session-based shopping cart with quantity updates and clearing.
- Shopping assistant that suggests products using local keyword and budget rules.
- Responsive layout and automated tests.

## Honest AI/model description
The assistant is a simple rule-based recommender, not a trained ML model or external generative AI API. Product data is hard-coded demo data. There is no login, payment, or real checkout.

## Run on macOS
Open the folder in VS Code, then Terminal → New Terminal:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5003. Keep the terminal open while using the site. Stop with Control+C.

If port 5003 is busy:
```bash
python -c "from app import app; app.run(host='127.0.0.1', port=5004, debug=False)"
```
Then open http://127.0.0.1:5004.

## Tests
```bash
python -m pytest -v
```

## 5-minute demo
1. Browse the catalog and search “headphones”.
2. Filter by Electronics and sort by rating.
3. Add products to cart and update quantities.
4. Ask the assistant: “Suggest study products under ₹1500”.
5. Explain keyword and budget matching, and clarify that it is rule-based.
6. Show automated tests and describe limitations.

## Architecture
Browser → Flask routes → catalog/search/filter/sort → rule-based recommendation engine and session cart → HTML response.

## Viva points
- Flask routes handle browser requests.
- Product data is a Python list of dictionaries.
- Search matches query words against product name, category, description and tags.
- The cart is held in Flask's signed session cookie, not a database.
- The assistant uses keyword matching and optional budget filtering.
- Limitations: sample data, no accounts/payments, no trained AI model, no live inventory.
