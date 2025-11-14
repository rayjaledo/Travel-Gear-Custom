from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "travelgear_secret"

# ======== SIMPLE CART STORAGE (List) ========
cart_items = []

# ======== DB CONNECTION ========
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ======== ROUTES ========
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/products')
def products():
    return render_template('products.html')

# View Cart
@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

# Checkout
@app.route('/checkout')
def checkout():
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("checkout.html", cart_items=cart_items, total=total)



# ======== SIGNUP ========
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "<h3>Username already exists. Try another.</h3>"
        finally:
            conn.close()
    return render_template('signup.html')

# ======== LOGIN ========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "<h3>Invalid credentials. Please try again.</h3>"
    return render_template('login.html')

# ======== LOGOUT ========
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ======== ADD TO CART ========
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    product = request.form.get('product')
    price = float(request.form.get('price', 0))
    quantity = int(request.form.get('quantity', 1))  # Default quantity = 1

    # If item exists, increase quantity instead of adding new row
    for item in cart_items:
        if item['product'] == product:
            item['quantity'] += quantity
            break
    else:
        cart_items.append({'product': product, 'price': price, 'quantity': quantity})

    return redirect(url_for('cart'))


@app.route('/update_quantity/<int:index>/<int:change>', methods=['POST'])
def update_quantity(index, change):
    if 'username' not in session:
        return redirect(url_for('login'))

    if 0 <= index < len(cart_items):
        if change == 0:
            cart_items[index]['quantity'] -= 1
        elif change == 1:
            cart_items[index]['quantity'] += 1

        if cart_items[index]['quantity'] < 1:
            cart_items[index]['quantity'] = 1

    return redirect(url_for('cart'))





# (rest of your code continues)



# ✅ REMOVE ITEM
@app.route('/remove_item/<int:index>', methods=['POST'])
def remove_item(index):
    if 'username' not in session:
        return redirect(url_for('login'))

    if 0 <= index < len(cart_items):
        cart_items.pop(index)
    return redirect(url_for('cart'))

# ✅ CLEAR CART
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cart_items.clear()
    return redirect(url_for('cart'))


# ======== PROCESS CHECKOUT ========
@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    if 'username' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    payment = request.form.get('payment')

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into orders table
    cursor.execute("""
        INSERT INTO orders (username, full_name, phone, address, payment, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session['username'], name, phone, address, payment, total))
    order_id = cursor.lastrowid

    # Insert each item into order_items table
    for item in cart_items:
        subtotal = item['price'] * item['quantity']
        cursor.execute("""
            INSERT INTO order_items (order_id, product, quantity, subtotal)
            VALUES (?, ?, ?, ?)
        """, (order_id, item['product'], item['quantity'], subtotal))

    conn.commit()
    conn.close()

    # Save order details in session for success page
    session['order_details'] = {
        'name': name,
        'phone': phone,
        'address': address,
        'payment': payment,
        'cart': cart_items.copy(),
        'total': total
    }

    cart_items.clear()
    return redirect(url_for('order_success'))


# ======== ORDER SUCCESS PAGE ========
# ======== ORDER SUCCESS PAGE ========
@app.route('/order-success')
def order_success():
    if 'username' not in session:
        return redirect(url_for('login'))

    order_details = session.get('order_details')
    if not order_details:
        return redirect(url_for('cart'))

    return render_template(
        "success.html",
        cart_items=order_details['cart'],
        total=order_details['total'],
        name=order_details['name'],
        phone=order_details['phone'],
        address=order_details['address'],
        payment=order_details['payment']
    )
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO messages (name, email, subject, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, subject, message))
    conn.commit()
    conn.close()

    return "<h3>Message sent successfully!</h3>"




if __name__ == '__main__':
    app.run(debug=True)
