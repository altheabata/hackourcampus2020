from flask import Flask, request
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
import requests

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:Jcp0tnFjhYtNmQjy@cluster0.qzgsg.mongodb.net/database?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route("/post-signup", methods=["POST"])
def post_signup():
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
    users.insert_one({"name": name, "email": email, "grad_year": grad_year, "college": college, "hashed_password": hashed_password})
    return "signup successful"

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
    return "<br>".join(subject_names)

@app.route("/course-list/<subject>")
def course_list(subject):
    response = requests.get("https://classes.cornell.edu/api/2.0/search/classes.json?roster=FA20&subject=" + subject)
    if not response:
        return "API call failed"
    courses = response.json()["data"]["classes"]
    subjects = [course["subject"] for course in courses]
    numbers = [course["catalogNbr"] for course in courses]
    titles = [course["titleLong"] for course in courses]
    return "work in progress"
#    return "<br>".join([subjects[i] + " " + numbers[i] + ": " + titles[i] for i in range(len(courses))])
