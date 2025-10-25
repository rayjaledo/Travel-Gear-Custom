from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "travelgear_secret"

# ==================== In-Memory Storage ====================
users = {}
cart_items = []

# ==================== ROUTES ====================

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

@app.route('/cart')
def cart():
    return render_template('cart.html', cart_items=cart_items)

# ==================== SIGNUP ====================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "<h3>Username already exists. Try another.</h3>"
        else:
            users[username] = password
            return redirect(url_for('login'))
    return render_template('signup.html')

# ==================== LOGIN ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "<h3>Invalid credentials. Please try again.</h3>"
    return render_template('login.html')

# ==================== LOGOUT ====================
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ==================== ADD TO CART ====================
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product = request.form['product']
    price = float(request.form['price'])
    cart_items.append({'product': product, 'price': price})
    return redirect(url_for('cart'))

# ==================== RUN APP ====================
if __name__ == '__main__':
    app.run(debug=True)
