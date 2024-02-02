from flask import Flask, render_template, request, redirect, url_for
import pymysql
import pymysql.cursors

app = Flask(__name__)

connection = pymysql.connect(
    host="10.100.33.60",
    user="mmcfowler",
    password="220878185",
    database="mmcfowler_haze",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


@app.route("/")
def index():
    return render_template("landing.html.jinja")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        Username = request.form["username"]
        Firstname = request.form["first_name"]
        Lastname = request.form["last_name"]
        DOB = request.form["dob"]
        Password = request.form["password"]
        cursor = connection.cursor()
        sql = "INSERT INTO User (Username, Firstname, Lastname, DOB, Password) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (Username, Firstname, Lastname, DOB, Password))
        connection.commit()
        cursor.close()
    return render_template("register.html.jinja")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        Username = request.form['username']
        Password = request.form['password']
        cursor = connection.cursor()
        
        sql = "SELECT * From User WHERE Username = %s and Password = %s"
        cursor.execute(sql, (Username, Password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return redirect(url_for('home'))
        else:
            return render_template("signin.html.jinja", error="Invalid username or password")
    return render_template("signin.html.jinja")


@app.route('/home')
def home():
    return render_template('home.html.jinja')



if __name__ == "__main__":
    app.run(debug=True)
