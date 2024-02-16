from flask import Flask, render_template, request, redirect, url_for, g
from pymysql.err import IntegrityError
import pymysql
import pymysql.cursors
import flask_login

app = Flask(__name__)
app.secret_key = "ewbugduihfqwcenp"
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True
    def __init__(self, id, username, ProfilePic):
        self.username = username
        self.id = id
        self.pfp = ProfilePic
    def get_id(self):
        return str(self.id)



def connect_db():
    return pymysql.connect(
        host="10.100.33.60",
        user="mmcfowler",
        password="220878185",
        database="mmcfowler_haze",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db    

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close() 



@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * From User WHERE ID = " + str(user_id))
    result = cursor.fetchone()
    get_db().commit()
    cursor.close()
    if result is None:
        return None
    return User(result["ID"], result["Username"], result["ProfilePic"])


@app.route("/")
def index():
    if flask_login.current_user.is_authenticated:
        return redirect("/home")
    return render_template("landing.html.jinja")


@app.route("/register", methods=["GET", "POST"])
def register():
    if flask_login.current_user.is_authenticated:
        return redirect("/home")
    if request.method == "POST":
        try:
            Username = request.form["username"]
            Firstname = request.form["first_name"]
            Lastname = request.form["last_name"]
            DOB = request.form["dob"]
            Password = request.form["password"]
            cursor = get_db().cursor()
            sql = "INSERT INTO User (Username, Firstname, Lastname, DOB, Password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (Username, Firstname, Lastname, DOB, Password))
            get_db().commit()
            cursor.close()
        except IntegrityError as e:
            error_message = "Error: Duplicate username. Please choose another username and try again."
            return render_template("register.html.jinja", error_message=error_message)
    return render_template("register.html.jinja")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if flask_login.current_user.is_authenticated:
        return redirect("/home")
    if request.method == "POST":
        Username = request.form["username"]
        Password = request.form["password"]
        cursor = get_db().cursor()
        sql = f"SELECT * From User WHERE Username = '{Username}'"
        cursor.execute(sql)
        user = cursor.fetchone()
        cursor.close()
        get_db().commit()
        if user and user["Password"] == Password:
            user = load_user(user["ID"])
            flask_login.login_user(user)
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"
            return render_template("signin.html.jinja", error=error)
    return render_template("signin.html.jinja")


@app.route("/home", methods=['POST', 'GET'])
@flask_login.login_required
def home():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Posts JOIN `User` ON Posts.User_ID = User.ID ORDER BY `timestamp`"
    cursor.execute(sql)
    posts = cursor.fetchall()
    cursor.close()
    return render_template("home.html.jinja", posts=posts)

@app.route('/post', methods=['POST'])
@flask_login.login_required
def create_post():
    description = request.form['Description']
    image_url = request.form['Image']
    user_id = flask_login.current_user.id
    sql = "INSERT INTO Posts (`User_ID`, `Description`, `Image`, `Timestamp`) VALUES (%s, %s, %s, NOW())"
    cursor = get_db().cursor()
    cursor.execute(sql, (user_id, description, image_url, ))
    get_db().commit()
    cursor.close()
    return redirect('/home')

if __name__ == "__main__":
    app.run(debug=True)
