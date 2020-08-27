from flask import Flask, request, session, render_template
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
import smtplib
from os import urandom
import requests
# to allow for simultaneous update in cloudshell
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:Jcp0tnFjhYtNmQjy@cluster0.qzgsg.mongodb.net/database?retryWrites=true&w=majority"
mongo = PyMongo(app)
app.secret_key = urandom(24)

# homepage route
@app.route('/')  
@app.route('/index', methods = ["GET", "POST"])
def index():
    return render_template('index.html', time=datetime.now())

# study groups page route
@app.route('/groups')
def groups():
    return render_template('groups.html', time=datetime.now())

@app.route("/post-signup", methods=["POST"])
def post_signup():
    # Save the user's information to the database
    name = request.form["name"]
    email = request.form["email"]
    grad_year = request.form["grad_year"]
    college = request.form["college"]
    password = request.form["password"]
    users = mongo.db.users
    if "email"[-12:] != "@cornell.edu":
        return "must use a cornell email"
    if len(users.find({"email": email})) > 0:
        return "email already taken"
    hashed_password = sha256_crypt.hash(password)
    verification_code = urandom(24).hex()
    while users.find_one({"verification_code": verification_code}):
        verification_code = urandom(24).hex()
    users.insert_one({"name": name, "email": email, "grad_year": grad_year, "college": college, "hashed_password": hashed_password, "verification_code": verification_code})
    # Send the verification email
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    from_address = "apf75@cornell.edu"
    server.login(from_address)
    text = "Subject: CornField email verification\n\nPlease follow this link to verify your email address: http://localhost:5000/verify/" + verification_code
    server.sendmail(from_address, email, text)
    server.quit()
    return "signup successful, verification email sent"

@app.route("/verify/<verification_code>")
def verify(verification_code):
    users = mongo.db.users
    user = users.find_one({"verification_code": verification_code})
    if not user:
        return "verification code invalid"
    users.update_one({"verification_code": verification_code}, {"$unset": {"verification_code": ""}})
    return "verification successful"

@app.route("/post-login", methods=["POST"])
def post_login():
    email = request.form["email"]
    password = request.form["password"]
    users = mongo.db.users
    user = users.find_one({"email": email})
    if sha256_crypt.verify(password, user["hashed_password"]):
        return "login successful"
    else:
        return "credentials do not match records"

@app.route("/subject-list")
def subject_list():
    response = requests.get("https://classes.cornell.edu/api/2.0/config/subjects.json?roster=FA20")
    if not response:
        return "API call failed"
    subjects = response.json()["data"]["subjects"]
    subject_names = [subject["descr"] for subject in subjects]
    return render_template("subjects.html", subjects=subject_names)
#    return "<br>".join(subject_names)

@app.route("/course-list/<subject>")
def course_list(subject):
    response = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA20&subject=" + subject)
    if not response:
        return "API call failed"
    courses = response.json()["data"]["classes"]
    numbers = [course["catalogNbr"] for course in courses]
    titles = [course["titleLong"] for course in courses]
    return "<br>".join([subject + " " + numbers[i] + ": " + titles[i] for i in range(len(courses))])

@app.route("/add-course/<subject>/<number>")
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
