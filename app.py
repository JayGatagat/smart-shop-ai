import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from shop_data import PRODUCTS, CATEGORIES, recommend, assistant_reply, get_product

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smart-shop-demo-key-change-me")

USERS = {}


def cart_count():
    return sum(session.get("cart", {}).values())


def current_user():
    return session.get("user")


def wishlist_ids():
    return [int(pid) for pid in session.get("wishlist", [])]


def wishlist_products():
    return [product for product in PRODUCTS if product["id"] in wishlist_ids()]


def cart_summary():
    cart_data, total = [], 0
    for pid, qty in session.get("cart", {}).items():
        product = get_product(int(pid))
        if product:
            line = product["price"] * qty
            total += line
            cart_data.append({"product": product, "qty": qty, "line": line})
    return cart_data, total


def render_home_context(**kwargs):
    context = {
        "user": current_user(),
        "wishlist_ids": wishlist_ids(),
        "cart_count": cart_count(),
    }
    context.update(kwargs)
    return context


@app.get("/")
def home():
    products = recommend(PRODUCTS, request.args.get("q", ""), request.args.get("category", "All"), request.args.get("sort", "featured"))
    return render_template(
        "index.html",
        products=products,
        categories=CATEGORIES,
        q=request.args.get("q", ""),
        category=request.args.get("category", "All"),
        sort=request.args.get("sort", "featured"),
        **render_home_context(),
    )


@app.get("/product/<int:pid>")
def product_detail(pid):
    product = get_product(pid)
    if not product:
        flash("Product not found.")
        return redirect(url_for("home"))

    related = [p for p in PRODUCTS if p["id"] != product["id"] and p["category"] == product["category"]]
    related.sort(key=lambda p: (-p["rating"], p["price"]))
    return render_template(
        "product.html",
        product=product,
        related=related[:3],
        **render_home_context(),
    )


@app.post("/add/<int:pid>")
def add(pid):
    if not get_product(pid):
        flash("Product not found.")
    else:
        cart = session.get("cart", {})
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        session["cart"] = cart
        flash("Product added to cart!")
    return redirect(request.referrer or url_for("home"))


@app.post("/wishlist/toggle/<int:pid>")
def toggle_wishlist(pid):
    if not current_user():
        flash("Please log in to save products to your wishlist.")
        return redirect(url_for("login"))

    saved = session.get("wishlist", [])
    pid_str = str(pid)
    if pid_str in saved:
        saved = [item for item in saved if item != pid_str]
        flash("Removed from wishlist.")
    else:
        saved.append(pid_str)
        flash("Added to wishlist.")
    session["wishlist"] = saved
    return redirect(request.referrer or url_for("home"))


@app.get("/wishlist")
def wishlist():
    if not current_user():
        flash("Please log in to view your wishlist.")
        return redirect(url_for("login"))
    return render_template("wishlist.html", products=wishlist_products(), **render_home_context())


@app.get("/cart")
def cart():
    cart_data, total = cart_summary()
    shipping = 0 if total >= 2500 else 149
    grand_total = total + shipping
    return render_template(
        "cart.html",
        items=cart_data,
        subtotal=total,
        shipping=shipping,
        total=grand_total,
        **render_home_context(),
    )


@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for pid in list(cart):
        try:
            qty = int(request.form.get("qty_" + pid, cart[pid]))
        except ValueError:
            qty = 1
        if qty <= 0:
            cart.pop(pid, None)
        else:
            cart[pid] = min(qty, 99)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.post("/cart/clear")
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("cart"))


@app.get("/checkout")
def checkout():
    if not current_user():
        flash("Please log in to continue to checkout.")
        return redirect(url_for("login"))

    items, subtotal = cart_summary()
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for("cart"))

    shipping = 0 if subtotal >= 2500 else 149
    total = subtotal + shipping
    return render_template(
        "checkout.html",
        items=items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        **render_home_context(),
    )


@app.post("/checkout")
def process_checkout():
    if not current_user():
        flash("Please log in to continue to checkout.")
        return redirect(url_for("login"))

    items, subtotal = cart_summary()
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for("cart"))

    shipping = 0 if subtotal >= 2500 else 149
    grand_total = subtotal + shipping
    session["last_order"] = {
        "order_id": f"SSAI-{uuid4().hex[:8].upper()}",
        "items": [{"name": item["product"]["name"], "qty": item["qty"], "line": item["line"]} for item in items],
        "subtotal": subtotal,
        "shipping": shipping,
        "total": grand_total,
        "customer": current_user()["name"],
    }
    session["cart"] = {}
    return redirect(url_for("order_success"))


@app.get("/order-success")
def order_success():
    order = session.get("last_order")
    if not order:
        return redirect(url_for("home"))
    return render_template("order_success.html", order=order, **render_home_context())


@app.get("/signup")
def signup_page():
    if current_user():
        return redirect(url_for("home"))
    return render_template("signup.html", **render_home_context())


@app.post("/signup")
def signup():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    if not name or not email or not password:
        flash("Please complete all signup fields.")
        return redirect(url_for("signup_page"))

    if email in USERS:
        flash("An account with this email already exists.")
        return redirect(url_for("signup_page"))

    USERS[email] = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
    }
    session["user"] = {"name": name, "email": email}
    session.setdefault("wishlist", [])
    flash("Account created successfully!")
    return redirect(url_for("home"))


@app.get("/login")
def login_page():
    if current_user():
        return redirect(url_for("home"))
    return render_template("login.html", **render_home_context())


@app.post("/login")
def login():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = USERS.get(email)
    if not user or not check_password_hash(user["password"], password):
        flash("Invalid email or password.")
        return redirect(url_for("login_page"))

    session["user"] = {"name": user["name"], "email": user["email"]}
    session.setdefault("wishlist", [])
    flash("Welcome back!")
    return redirect(url_for("home"))


@app.get("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    question = request.form.get("question", "")
    answer = assistant_reply(question, PRODUCTS) if request.method == "POST" else ""
    return render_template("assistant.html", question=question, answer=answer, **render_home_context())


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5003")),
        debug=os.environ.get("DEBUG", "false").lower() == "true",
    )
