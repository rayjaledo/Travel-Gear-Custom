from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ===================== ROUTES =====================

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('contacts.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')


# ===================== ADD TO CART =====================

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product = request.form['product']
    price = request.form['price']

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'product': product, 'price': price})
    return redirect(url_for('cart'))


# ===================== RUN APP =====================
if __name__ == '__main__':
    app.run(debug=True)
