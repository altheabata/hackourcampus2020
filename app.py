from flask import Flask, request, session, render_template, redirect
from flask_pymongo import PyMongo
import smtplib
from os import urandom
import requests
import model
# to allow for simultaneous update in cloudshell
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:Jcp0tnFjhYtNmQjy@cluster0.qzgsg.mongodb.net/database?retryWrites=true&w=majority"
mongo = PyMongo(app)
app.secret_key = "d8e5f254ff33cc5c53107093e945c90a27ef999085d0496b"


# Limit each page to either logged in or logged out users
def require_logged_in(route):
    def wrapper(**kwargs):
        if "email" in session:
            return route(**kwargs)
        return redirect("/login")
    wrapper.__name__ = route.__name__
    return wrapper

def require_logged_out(route):
    def wrapper(**kwargs):
        if "email" in session:
            return redirect("/groups")
        return route(**kwargs)
    wrapper.__name__ = route.__name__
    return wrapper
    


# homepage route
@app.route('/')  
@app.route('/index', methods = ["GET", "POST"])
@require_logged_out
def index():
    print(session)
    return render_template('index.html', time=datetime.now())

# study groups page route
@app.route('/groups')
@require_logged_in
def groups():
    return render_template('groups.html', time=datetime.now())

@app.route("/signup")
@require_logged_out
def signup():
    return render_template("signup.html")

@app.route("/post-signup", methods=["POST"])
@require_logged_out
def post_signup():
    # Save the user's information to the database
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    grad_year = request.form["grad_year"]
    college = request.form["college"]
    password = request.form["password"]
    users = mongo.db.users
    if email[-12:] != "@cornell.edu":
        return "must use a cornell email"
    if users.find_one({"email": email}):
        return "email already taken"
    hashed_password = sha256_crypt.hash(password)
    verification_code = urandom(24).hex()
    while users.find_one({"verification_code": verification_code}): # Make sure the verification code is unique
        verification_code = urandom(24).hex()
    users.insert_one({"first_name": first_name, "last_name": last_name, "email": email, "grad_year": grad_year, "college": college, "hashed_password": hashed_password, "verification_code": verification_code})
    # Send the verification email
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    from_address = "cornfieldapp@gmail.com"
    server.login(from_address, "digjid-Dehge9-cambot")
    text = "Subject: CornField email verification\n\nPlease follow this link to verify your email address: http://localhost:5000/verify/" + verification_code
    server.sendmail(from_address, email, text)
    server.quit()
    return "signup successful, verification email sent"

@app.route("/verify/<verification_code>")
@require_logged_out
def verify(verification_code):
    users = mongo.db.users
    user = users.find_one({"verification_code": verification_code})
    if not user:
        return "verification code invalid"
    users.update_one({"verification_code": verification_code}, {"$unset": {"verification_code": ""}})
    session["email"] = user["email"]
    print("successfully verified " + user["email"])
    return redirect("/groups")

@app.route("/login")
@require_logged_out
def login():
    return render_template("login.html")

@app.route("/post-login", methods=["POST"])
@require_logged_out
def post_login():
    email = request.form["email"]
    password = request.form["password"]
    result = model.attempt_login(email, password, mongo)
    if result["success"]:
        session["email"] = email
        return redirect("/groups")
    else:
        return result["error"]

@app.route("/post-login-ios", methods=["POST"])
@require_logged_out
def post_login_ios():
    email = request.form["email"]
    password = request.form["password"]
    result = model.attempt_login(email, password, mongo)
    return result

@app.route("/subjects")
@require_logged_in
def subject_list():
    response = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json?roster=FA20")
    if not response:
        return "API call failed"
    subjects = response.json()["data"]["subjects"]
    subject_names = [subject["descr"] for subject in subjects]
    subject_abbrievs = [subject["value"] for subject in subjects]
    subjects = [{"name": subject_names[i], "abbrieviation": subject_abbrievs[i]} for i in range(len(subjects))]
    return render_template("subjects.html", subjects=subjects)
#    return "<br>".join(subject_names)

@app.route("/courses/<subject>")
@require_logged_in
def course_list(subject):
    response = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA20&subject=" + subject)
    if not response:
        return "API call failed"
    courses = response.json()["data"]["classes"]
    numbers = [course["catalogNbr"] for course in courses]
    names = [course["titleLong"] for course in courses]
    courses = [{"number": numbers[i], "name": names[i]} for i in range(len(courses))]
    return render_template("courses.html", courses=courses, subject=subject)
#    return "<br>".join([subject + " " + numbers[i] + ": " + titles[i] for i in range(len(courses))])

@app.route("/add-course/<subject>/<number>")
@require_logged_in
def add_course(subject, number):
    response = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA20&subject=" + subject)
    if not response:
        return "API call failed"
    course_numbers = response.json()["data"]["classes"]["catalogNbr"]
    if number not in course_numbers:
        return "course number invalid"
    users = mongo.db.users
    return "work in progress"
#    user =
