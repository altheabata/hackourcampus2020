from flask import Flask, request, session, render_template, redirect
from flask_pymongo import PyMongo
from os import urandom
import requests
import model
# to allow for simultaneous update in cloudshell
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:Jcp0tnFjhYtNmQjy@cluster0.qzgsg.mongodb.net/database?retryWrites=true&w=majority"
mongo = PyMongo(app)
app.secret_key = "d8e5f254ff33cc5c53107093e945c90a27ef999085d0496b"


# Pass the time into every route automatically (to sync CSS)
@app.context_processor
def inject_datetime():
    return dict(time=datetime.now())


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
    return render_template('index.html')

# study groups page route
@app.route('/groups')
@require_logged_in
def groups():
    return render_template('groups.html')

@app.route("/signup")
@require_logged_out
def signup():
    return render_template("signup.html")

@app.route("/post-signup", methods=["POST"])
@require_logged_out
def post_signup():
    result = model.attempt_signup(request.form, mongo)
    if result["success"]:
        return "Check your inbox (and spam folder) for a verification email."
    else:
        return result["error"]

@app.route("/post-signup-ios", methods=["POST"])
@require_logged_out
def post_signup_ios():
    result = model.attempt_signup(request.form, mongo)
    return result

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
    result = model.attempt_login(request.form, mongo)
    if result["success"]:
        session["email"] = request.form["email"]
        return redirect("/groups")
    else:
        return result["error"]

@app.route("/post-login-ios", methods=["POST"])
@require_logged_out
def post_login_ios():
    result = model.attempt_login(request.form, mongo)
    return result

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html', time=datetime.now())

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
