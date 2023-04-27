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
                    "type": user[4]
                }
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
@app.route('/products')
@login_required
def products():
    print(session)
    return render_template('products.html')

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/reciept')
@login_required
def reciept():
    return render_template('receipt.html')

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

@app.route('/returns')
@login_required
def returns():
    return render_template('returns.html')

#endregion

if __name__ == '__main__':
    app.run(debug=True)