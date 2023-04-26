from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from conn import sql_username, sql_password

app = Flask(__name__)

conn_str = f"mysql://{sql_username()}:{sql_password()}@localhost:3306/retailer"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

# routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/reciept')
def reciept():
    return render_template('receipt.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/returns')
def returns():
    return render_template('returns.html')

if __name__ == '__main__':
    app.run(debug=True)