from shop_data import PRODUCTS, recommend, assistant_reply, get_product

def test_catalog():
    assert len(PRODUCTS) >= 5

def test_get_product():
    assert get_product(1)["name"] == "Wireless Headphones"
    assert get_product(999) is None

def test_search():
    assert any("Headphones" in p["name"] for p in recommend(PRODUCTS, "headphones"))

def test_assistant_budget():
    assert "suggestions" in assistant_reply("Suggest study products under ₹1500", PRODUCTS)
