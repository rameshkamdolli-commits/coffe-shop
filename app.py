from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from functools import wraps
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"
DB_PATH = Path(__file__).with_name("coffee_shop.db")
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"  # Change this before deployment.

PRODUCTS = [
    ("Masala Tea","Tea",20,"Indian tea with aromatic spices."),
    ("Ginger Tea","Tea",15,"Hot tea with fresh ginger."),
    ("Lemon Tea","Tea",15,"Refreshing lemon tea."),
    ("Green Tea","Tea",25,"Light and soothing green tea."),
    ("Espresso","Hot Coffee",90,"Strong Italian-style coffee."),
    ("Americano","Hot Coffee",120,"Espresso balanced with hot water."),
    ("Cappuccino","Hot Coffee",150,"Espresso with steamed milk foam."),
    ("Cafe Latte","Hot Coffee",160,"Smooth espresso and creamy milk."),
    ("Caramel Latte","Hot Coffee",190,"Creamy coffee with caramel."),
    ("Chocolate Mocha","Hot Coffee",180,"Espresso, chocolate and milk."),
    ("Vanilla Latte","Hot Coffee",180,"Velvety latte with vanilla."),
    ("Hazelnut Coffee","Hot Coffee",200,"Coffee with toasted hazelnut notes."),
    ("Cold Coffee","Cold Drinks",160,"Chilled and refreshing coffee."),
    ("Iced Americano","Cold Drinks",140,"Espresso served over ice."),
    ("Iced Mocha","Cold Drinks",190,"Cold coffee blended with chocolate."),
    ("Caramel Frappuccino","Cold Drinks",220,"Blended iced coffee with caramel."),
    ("Chocolate Brownie","Desserts",120,"Soft, rich chocolate brownie."),
    ("Cheesecake","Desserts",180,"Rich and creamy cheesecake."),
    ("Chocolate Muffin","Desserts",90,"Fresh-baked chocolate muffin."),
    ("Chocolate Donut","Desserts",80,"Chocolate-glazed donut."),
    ("Croissant","Desserts",100,"Buttery, flaky bakery croissant."),
    ("Samosa","Snacks",15,"Crispy potato samosa."),
    ("Masala Maggi","Snacks",40,"Hot and tasty masala noodles."),
    ("Veg Sandwich","Snacks",50,"Fresh vegetable sandwich."),
    ("Bread Omelette","Snacks",50,"Omelette served with toasted bread."),
    ("French Fries","Snacks",110,"Crispy golden fries."),
    ("Garlic Bread","Snacks",120,"Toasted bread with garlic."),
    ("Cheese Sandwich","Snacks",160,"Toasted sandwich with melted cheese.")
]

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, category TEXT,
            price INTEGER, description TEXT, active INTEGER DEFAULT 1)""")
        con.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT,
            address TEXT, items TEXT, total INTEGER, status TEXT DEFAULT 'Received',
            created_at TEXT)""")
        for p in PRODUCTS:
            con.execute("INSERT OR IGNORE INTO products(name,category,price,description) VALUES(?,?,?,?)", p)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_cart_count():
    return {"cart_count": sum(session.get("cart", {}).values())}

@app.route("/")
def home():
    with db() as con:
        products = con.execute("SELECT * FROM products WHERE active=1 ORDER BY category,name").fetchall()
    return render_template("index.html", products=products)

@app.route("/menu")
def menu():
    with db() as con:
        products = con.execute("SELECT * FROM products WHERE active=1 ORDER BY category,name").fetchall()
    return render_template("menu.html", products=products)

@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    ids = [int(k) for k,v in cart_data.items() if int(v)>0]
    items, total = [], 0
    if ids:
        with db() as con:
            rows = con.execute(f"SELECT * FROM products WHERE id IN ({','.join('?' for _ in ids)}) AND active=1", ids).fetchall()
        for p in rows:
            qty = int(cart_data.get(str(p["id"]), 0))
            subtotal = p["price"] * qty
            total += subtotal
            items.append({"product":p,"qty":qty,"subtotal":subtotal})
    return render_template("cart.html", items=items, total=total)

@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    with db() as con:
        product = con.execute("SELECT id FROM products WHERE id=? AND active=1",(product_id,)).fetchone()
    if product:
        cart_data = session.get("cart", {})
        cart_data[str(product_id)] = int(cart_data.get(str(product_id),0)) + 1
        session["cart"] = cart_data
        flash("Item added to your cart.")
    return redirect(request.referrer or url_for("menu"))

@app.post("/cart/update")
def update_cart():
    cart_data = session.get("cart", {})
    for key, value in request.form.items():
        if key.startswith("qty_"):
            pid = key[4:]
            try: qty = max(0, min(99, int(value)))
            except ValueError: qty = 0
            if qty: cart_data[pid] = qty
            else: cart_data.pop(pid, None)
    session["cart"] = cart_data
    return redirect(url_for("cart"))

@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(product_id), None)
    session["cart"] = cart_data
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET","POST"])
def checkout():
    cart_data = session.get("cart", {})
    if request.method == "POST":
        customer = request.form.get("customer","").strip()
        phone = request.form.get("phone","").strip()
        address = request.form.get("address","").strip()
        if not customer or not phone or not address:
            flash("Please fill in your name, phone and address.")
            return redirect(url_for("checkout"))
        ids = [int(k) for k,v in cart_data.items() if int(v)>0]
        if not ids:
            flash("Your cart is empty.")
            return redirect(url_for("menu"))
        with db() as con:
            rows = con.execute(f"SELECT * FROM products WHERE id IN ({','.join('?' for _ in ids)}) AND active=1", ids).fetchall()
            line_items, total = [], 0
            for p in rows:
                qty = int(cart_data.get(str(p["id"]),0))
                subtotal = p["price"]*qty
                total += subtotal
                line_items.append(f'{p["name"]} x {qty} = Rs. {subtotal}')
            cur = con.execute("INSERT INTO orders(customer,phone,address,items,total,status,created_at) VALUES(?,?,?,?,?,?,?)",
                (customer,phone,address," | ".join(line_items),total,"Received",datetime.now().strftime("%d-%m-%Y %I:%M %p")))
            order_id = cur.lastrowid
        session["cart"] = {}
        return redirect(url_for("bill", order_id=order_id))
    cart_items = []
    total = 0
    ids = [int(k) for k,v in cart_data.items() if int(v)>0]
    if ids:
        with db() as con:
            rows = con.execute(f"SELECT * FROM products WHERE id IN ({','.join('?' for _ in ids)}) AND active=1",ids).fetchall()
        for p in rows:
            qty = int(cart_data[str(p["id"])])
            total += p["price"]*qty
            cart_items.append({"product":p,"qty":qty,"subtotal":p["price"]*qty})
    return render_template("checkout.html", items=cart_items,total=total)

@app.route("/bill/<int:order_id>")
def bill(order_id):
    with db() as con:
        order = con.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone()
    if not order: return "Bill not found",404
    return render_template("bill.html", order=order)

@app.route("/about")
def about(): return render_template("about.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        flash("Thanks! Your message has been received in this demo.")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message","").lower()
    if any(x in message for x in ["hello","hi","hey"]):
        answer = "Hello! Welcome to Chai & Coffee ☕ What would you like to explore?"
    elif "recommend" in message or "suggest" in message:
        answer = "Try a Cappuccino (₹150) with a Chocolate Brownie (₹120), or a Caramel Latte (₹190) if you like sweet coffee."
    elif "strong" in message:
        answer = "For a strong coffee, try Espresso (₹90) or Americano (₹120)."
    elif "cold" in message or "iced" in message:
        answer = "Our chilled choices include Cold Coffee ₹160, Iced Americano ₹140, Iced Mocha ₹190 and Caramel Frappuccino ₹220."
    elif "dessert" in message or "cake" in message or "brownie" in message:
        answer = "Desserts include Brownie ₹120, Cheesecake ₹180, Chocolate Muffin ₹90, Donut ₹80 and Croissant ₹100."
    elif "price" in message or "cost" in message:
        answer = "Tea starts at ₹15, coffee at ₹90, desserts at ₹80 and snacks at ₹15. Visit Menu for exact prices."
    elif "menu" in message or "items" in message:
        answer = "We serve Indian tea, hot coffee, cold drinks, desserts and snacks. Open the Menu page to browse and add items to your cart."
    elif "cart" in message or "order" in message:
        answer = "Add items from the Menu page, then open Cart to update quantities and proceed to checkout."
    else:
        answer = "I can help with menu items, prices, strong or sweet coffee, cold drinks, desserts and ordering. Try: 'Suggest a coffee' or 'What cold drinks do you have?'"
    return jsonify({"reply":answer})

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username")==ADMIN_USER and request.form.get("password")==ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin username or password.")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None)
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    with db() as con:
        products = con.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        orders = con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 50").fetchall()
        stats = {
            "products": con.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0],
            "orders": con.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "revenue": con.execute("SELECT COALESCE(SUM(total),0) FROM orders").fetchone()[0]
        }
    return render_template("admin.html",products=products,orders=orders,stats=stats)

@app.post("/admin/product/add")
@admin_required
def admin_add_product():
    try:
        with db() as con:
            con.execute("INSERT INTO products(name,category,price,description) VALUES(?,?,?,?)",
                (request.form["name"].strip(),request.form["category"],int(request.form["price"]),request.form.get("description","").strip()))
        flash("Product added.")
    except Exception:
        flash("Could not add product. Check that the name is unique and price is valid.")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/product/<int:pid>/toggle")
@admin_required
def admin_toggle_product(pid):
    with db() as con:
        con.execute("UPDATE products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?",(pid,))
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/order/<int:oid>/status")
@admin_required
def admin_order_status(oid):
    status = request.form.get("status","Received")
    if status not in ["Received","Preparing","Ready","Delivered","Cancelled"]: status="Received"
    with db() as con: con.execute("UPDATE orders SET status=? WHERE id=?",(status,oid))
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
