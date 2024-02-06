from flask import Flask, render_template, request, redirect, url_for, session
from pymysql.err import IntegrityError
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'OneLit_3G'

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
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
        except IntegrityError as e:
            error_message = "Error: Duplicate username. Please choose another username and try again."
            return render_template("register.html.jinja", error_message=error_message)
    return render_template("register.html.jinja")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        Username = request.form["username"]
        Password = request.form["password"]
        cursor = connection.cursor()
        sql = f"SELECT * From User WHERE Username = '{Username}'"
        cursor.execute(sql)
        user = cursor.fetchone()
        cursor.close()
        connection.commit()
        if user and user['Password'] == Password:
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"
            return render_template("signin.html.jinja", error=error)
    return render_template("signin.html.jinja")


@app.route("/home")
def home():
    return render_template("home.html.jinja")


if __name__ == "__main__":
    app.run(debug=True)
