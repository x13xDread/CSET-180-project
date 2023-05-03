from flask import Flask, render_template, request, session, redirect
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from conn import sql_username, sql_password

app = Flask(__name__)

conn_str = f"mysql://{sql_username()}:{sql_password()}@localhost:3306/retailer"
app.secret_key='this is def very secret oooooooooooo'
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

#login required function
def login_required(next_func):
    def inner_func(**kwargs):
        if "user" in session:
            return next_func(**kwargs)
        return redirect("/login")
    inner_func.__name__ = next_func.__name__
    return inner_func

# routes
@app.route('/')
def index():
    return render_template('index.html')

#region login routes
@app.route('/login',methods=["GET"])
def login():
    return render_template('login.html')

@app.route('/login',methods=["POST"])
def post_login():
    try:
        user = conn.execute(
            text("SELECT * from users where username = :username"),
            request.form
        ).one_or_none()

        if user is None:
            error = "User does not exist!"
            return render_template('login.html', error=error, success=None)
        else:
            if user[3] == request.form['password']:
                session['user'] = {
                    "username": user[2],
                    "name": user[0],
                    "email": user[1],
                    "type": user[4]
                }
                session['cart'] = {}
                return render_template('index.html', error=None, success="Logged in")
            else:
                error = "Wrong password!"
                return render_template('login.html', error=error, success=None)

    except Exception as e:
        error = e.args[0]
        print(f"ERROR: {error}")
        return render_template('login.html', error=error, success=None)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
#endregion

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

#region protected routes
@app.route('/products', methods=['POST', 'GET'])
@login_required
def products():
    if(request.method == 'POST'):
        session['cart'] = request.get_json()
        print(session['cart'])
    products = conn.execute(text('Select * from products;'))
    vendors = conn.execute(text('Select name, email from users where type="vendor";')).fetchall()
    return render_template('products.html',products=products,vendors=vendors)

@app.route('/cart')
@login_required
def cart():
    if(request.method == 'POST'):
        session['cart'] = request.get_json()
        print(session['cart'])
    products = conn.execute(text('Select * from products;')).fetchall()
    vendors = conn.execute(text('Select name, email from users where type="vendor";')).fetchall()
    current_total = 0
    
    for item in session['cart']:
        for product in products:
            if int(item) == product[1]:
                current_total = round(current_total + (product[-1]*session['cart'][item]),2)
            
    return render_template('cart.html',products=products,vendors=vendors,current_total=current_total)

@app.route('/checkout')
@login_required
def checkout():
    current_total = 0
    products = conn.execute(text('Select * from products;')).fetchall()
    for item in session['cart']:
        for product in products:
            if int(item) == product[1]:
                current_total = round(current_total + (product[-1]*session['cart'][item]),2)
    return render_template('checkout.html',current_total=current_total)

@app.route('/receipt', methods=["POST"])
@login_required
def reciept():
    # create order
    conn.execute(text(f"INSERT INTO orders (email) values (\"{session['user']['email']}\")"))
    conn.commit()
    # get new order id
    order_id = conn.execute(text("select order_id from orders order by order_id desc limit 1;")).one_or_none()[0]
    print(order_id)
    # add order items
    for item in session['cart']:
        if session['cart'][item] > 0:
            for x in range(0,session['cart'][item]):
                conn.execute(text(f"INSERT INTO order_items (order_id, product_id) values ({order_id}, {item})"))
                conn.commit()
    current_total = 0
    products = conn.execute(text('Select * from products;')).fetchall()
    for item in session['cart']:
        for product in products:
            if int(item) == product[1]:
                current_total = round(current_total + (product[-1]*session['cart'][item]),2)
    session['cart'] = {}
    return render_template('receipt.html',current_total=current_total, order_id=order_id)

@app.route('/orders')
@login_required
def orders():
    if session['user']['type'] == 'admin':
        orders = conn.execute(text(f"select * from orders;"))
    else:
        orders = conn.execute(text(f"select * from orders where email = '{session['user']['email']}';"))
    return render_template('orders.html', orders=orders)

@app.route('/returns')
@login_required
def returns():
    return render_template('returns.html')

#endregion

if __name__ == '__main__':
    app.run(debug=True)