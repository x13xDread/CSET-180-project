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

#region cart checkout and receipt


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
#endregion

#region orders
@app.route('/orders')
@login_required
def orders():
    if session['user']['type'] == 'admin':
        orders = conn.execute(text(f"select * from orders;"))
    else:
        orders = conn.execute(text(f"select * from orders where email = '{session['user']['email']}';"))
    return render_template('orders.html', orders=orders)

@app.route('/orders/change_status', methods=['POST'])
@login_required
def change_order_status():
    if session['user']['type'] == 'admin':
        conn.execute(text(f"update orders set status = :status where order_id = :order_id;"),request.form)
        conn.commit()
    return redirect('/orders')

@app.route('/orders/cancel', methods=['POST'])
@login_required
def cancel_order():
    if session['user']['type'] == 'admin':
        # delete all order items with order id
        conn.execute(text(f"delete from order_items where order_id = :order_id;"),request.form)
        conn.commit()
        #delete parent order
        conn.execute(text(f"delete from orders where order_id = :order_id;"),request.form)
        conn.commit()
    return redirect('/orders')
#endregion

#region returns
@app.route('/returns')
@login_required
def returns():
    if session['user']['type'] == 'admin':
        returns = conn.execute(text(f"select * from returns;"))
    else:
        returns = conn.execute(text(f"select * from returns where email = '{session['user']['email']}';"))
    return render_template('returns.html', returns=returns)

@app.route('/returns/new',methods=["POST"])
@login_required
def new_return():
    params = request.form.to_dict()
    if params == {}:
        print("Error no params!")
        return redirect("/orders")
    return render_template('new_return.html',order_id=params['order_id'])

@app.route('/returns/process',methods=["POST"])
@login_required
def process_new_return():
    params = request.form.to_dict()
    if params == {}:
        print("Error no params!")
        return redirect("/orders")
    conn.execute(text(f"INSERT INTO returns (order_id, email, title, return_description, demand) values (:order_id, '{session['user']['email']}', :title, :description, :demand)"), request.form)
    conn.commit()
    return redirect("/returns")
#endregion


#region products
@app.route('/products', methods=['POST', 'GET'])
@login_required
def products():
    if(request.method == 'POST'):
        session['cart'] = request.get_json()
        print(session['cart'])
    products = conn.execute(text('Select * from products;'))
    vendors = conn.execute(text('Select name, email from users where type="vendor";')).fetchall()
    return render_template('products.html',products=products,vendors=vendors)

@app.route('/products/new', methods=['POST', 'GET'])
@login_required
def new_product():
    if request.method == "POST":
        conn.execute(
                text("INSERT INTO products (product_name, email, product_description, inventory, price) values (:product_name, :email, :product_description, :inventory, :price)"),
                request.form
            )
        conn.commit()
    return redirect('/products')

@app.route('/products/edit', methods=['POST'])
@login_required
def edit_product():
   product = conn.execute(text("select * from products where product_id = :product_id"),request.form).one_or_none()
   return render_template('edit_product.html', product=product)

@app.route('/products/edit/process', methods=['POST'])
@login_required
def process_product_change():
    if session['user']['type'] == 'admin' or session['user']['type'] == 'vendor':
        conn.execute(text(f"update products set product_name = :product_name, product_description = :product_description, inventory = :inventory, price = :price where product_id = :product_id;"),request.form)
        conn.commit()
    return redirect('/products')

# do after reviews
@app.route('/products/delete', methods=['POST'])
@login_required
def delete_product():
   return redirect('/products')
#endregion

@app.route('/products/reviews')
def reviews():
    reviews = conn.execute(text('Select * from product_reviews;'))
    return render_template('reviews.html',reviews=reviews)
        


if __name__ == '__main__':
    app.run(debug=True)