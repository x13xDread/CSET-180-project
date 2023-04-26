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
# region registration routes
@app.route('/registration', methods=['GET'])
def registration():
    return render_template('registration.html')

@app.route('/registration', methods=['POST'])
def post_registration():
    try:
        conn.execute(
            text("INSERT INTO users (name, email, username, password, type) values (:name, :email, :username, :password, :type)"),
            request.form
        )
        conn.commit()
        return render_template('index.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('registration.html', error=error, success=None)

# endregion
@app.route('/returns')
def returns():
    return render_template('returns.html')

if __name__ == '__main__':
    app.run(debug=True)