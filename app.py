from flask import Flask, render_template, request, redirect, session
import pymysql
from functools import wraps
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "foodshare_secret"

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="foodshare",
        cursorclass=pymysql.cursors.Cursor
    )

# ---------------- LOGIN REQUIRED ----------------
def login_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect('/login')
            if role and session.get('role') != role:
                return redirect('/')
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ---------------- HOME ----------------
@app.route('/')
def index():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM food")
    meals = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT restaurant_id) FROM food")
    restaurants = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM food WHERE status='available'")
    available = cur.fetchone()[0]

    db.close()

    return render_template(
        'index.html',
        meals=meals,
        restaurants=restaurants,
        available=available
    )

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO users (name,email,password,role)
            VALUES (%s,%s,%s,%s)
        """, (
            request.form['name'],
            request.form['email'],
            request.form['password'],
            request.form['role']
        ))

        db.commit()
        db.close()
        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form['email'], request.form['password'])
        )

        user = cur.fetchone()
        db.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]
            return redirect(f"/{user[4]}")

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RESTAURANT ----------------
@app.route('/restaurant', methods=['GET','POST'])
@login_required(role='restaurant')
def restaurant():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO food
            (restaurant_id, food_name, quantity, pickup_time, expiry_time, description)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            request.form['food_name'],
            request.form['quantity'],
            request.form['pickup_time'],
            request.form['expiry_time'],
            request.form['description']
        ))

        db.commit()
        db.close()

    return render_template('restaurant/dashboard.html')

# ---------------- AVAILABLE FOOD ----------------
@app.route('/available-food')
def available_food():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT food.id, food.food_name, food.quantity,
               food.pickup_time, food.expiry_time,
               food.description, users.name
        FROM food
        JOIN users ON food.restaurant_id = users.id
        WHERE food.status='available'
    """)

    food = cur.fetchall()
    db.close()

    return render_template('available_food.html', food=food)

# ---------------- COLLECT ----------------
@app.route('/collect/<int:id>')
@login_required()
def collect(id):
    db = get_db()
    cur = db.cursor()

    cur.execute("UPDATE food SET status='collected' WHERE id=%s", (id,))
    db.commit()
    db.close()

    return redirect('/available-food')

# ---------------- OTHER ROLES ----------------
@app.route('/delivery')
@login_required(role='delivery')
def delivery():
    return render_template('delivery/dashboard.html')

@app.route('/beneficiary')
@login_required(role='beneficiary')
def beneficiary():
    return render_template('beneficiary/dashboard.html')

@app.route('/admin')
@login_required(role='admin')
def admin():
    return render_template('admin/dashboard.html')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)



app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

