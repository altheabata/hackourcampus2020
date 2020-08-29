from flask import Flask, request, session, render_template, redirect
from flask_pymongo import PyMongo
from os import urandom
import requests
from bson import ObjectId
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
    


# homepage route LOGGED OUT
@app.route('/')  
@app.route('/index', methods = ["GET", "POST"])
@require_logged_out
def index():
    print(session)
    return render_template('index.html')

# homepage route LOGGED IN
@app.route('/homepage')
def homepage():
    return render_template('logged-in-homepage.html')

# study groups page route
@app.route('/groups')
@require_logged_in
def groups():
    groups = mongo.db.groups
    joined_groups = list(groups.find({"members": session["email"]}))
    users = mongo.db.users
    organizers = [users.find_one({"email": group["organizer"]}) for group in joined_groups]
    return render_template('groups.html', groups=joined_groups, organizers=organizers)

# sign up route
@app.route("/signup")
@require_logged_out
def signup():
    return render_template("signup.html")

# study tips route
@app.route("/studytips")
@require_logged_in
def studytips():
    return render_template("studytips.html")

# connect route
@app.route("/connect")
@require_logged_in
def connect():
    return render_template("connect.html")

# profile route
@app.route("/profile")
@require_logged_in
def profile():
    return render_template("profile.html")

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

# login route
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

# logout route
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

@app.route("/course/<subject>/<course_number>/")
@require_logged_in
def course(subject, course_number):
    # Get the course title from the API
    response = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA20&subject=" + subject)
    if response:
        courses = response.json()["data"]["classes"]
        for course in courses:
            if course["catalogNbr"] == course_number:
                course_title = course["titleLong"]
                break
    # Find groups for the given course
    groups = mongo.db.groups
    relevent_groups = list(groups.find({"subject": subject, "course_number": course_number}))
    users = mongo.db.users
    organizers = [users.find_one({"email": group["organizer"]}) for group in relevent_groups]
    if course_title:
        return render_template("course.html", subject=subject, number=course_number, course_title=course_title, groups=relevent_groups, organizers=organizers)
    else:
        return render_template("course.html", subject=subject, number=course_number, groups=relevent_groups, organizers=organizers)

@app.route("/start-group/<subject>/<course_number>")
@require_logged_in
def start_group(subject, course_number):
    return render_template("start-group.html", subject=subject, number=course_number)

@app.route("/post-start-group/<subject>/<course_number>", methods=["POST"])
@require_logged_in
def post_start_group(subject, course_number):
    groups = mongo.db.groups
    member_cap = int(request.form["member_cap"])
    groups.insert_one({"subject": subject, "course_number": course_number, "member_cap": member_cap, "members": [session["email"]], "organizer": session["email"]})
    return redirect("/groups")

@app.route("/join-group/<group_id>")
@require_logged_in
def join_group(group_id):
    groups = mongo.db.groups
    group = groups.find_one({"_id": ObjectId(group_id)})
    if not group:
        return redirect("/subjects")
    if len(group["members"]) >= group["member_cap"]:
        return "this group is full"
    if session["email"] in group["members"]:
        return "you're already a member of this group"
    groups.update_one({"_id": group["_id"]}, {"$push": {"members": session["email"]}})
    return redirect("/groups")

@app.route("/group/<group_id>")
@require_logged_in
def group(group_id):
    groups = mongo.db.groups
    group = groups.find_one({"_id": ObjectId(group_id)})
    users = mongo.db.users
    organizer = users.find_one({"email": group["organizer"]})
    members = users.find({"email": {"$in": group["members"]}})
    return render_template("group.html", group=group, organizer=organizer, members=members)
