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

if __name__ == '__main__':
    app.run(debug=True)