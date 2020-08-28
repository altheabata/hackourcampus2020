from passlib.hash import sha256_crypt # For hashing and verifying passwords
import smtplib # For sending email-verification emails

def attempt_login(form, mongo):
    email = form["email"]
    password = form["password"]
    users = mongo.db.users
    user = users.find_one({"email": email})
    if not user:
        return {"success": False, "error": "credentials do not match records"}
    if sha256_crypt.verify(password, user["hashed_password"]):
        if "verification_code" in user:
            return {"success": False, "error": "account unverified"}
        print(email + " logged in successfully")
        return {"success": True}
    else:
        return {"success": False, "error": "credentials do not match records"}

def attempt_signup(form, mongo):
    # Save the user's information to the database
    first_name = form["first_name"]
    last_name = form["last_name"]
    email = form["email"]
    grad_year = form["grad_year"]
    college = form["college"]
    password = form["password"]
    users = mongo.db.users
    if email[-12:] != "@cornell.edu":
        return {"success": False, "error": "must use a cornell email"}
    if users.find_one({"email": email}):
        return {"success": False, "error": "email already taken"}
    hashed_password = sha256_crypt.hash(password)
    verification_code = urandom(24).hex()
    while users.find_one({"verification_code": verification_code}): # Make sure the verification code is unique
        verification_code = urandom(24).hex()
    users.insert_one({"first_name": first_name, "last_name": last_name, "email": email, "grad_year": grad_year, "college": college, "hashed_password": hashed_password, "verification_code": verification_code})
    # Send the verification email
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    from_address = "cornfieldapp@gmail.com"
    server.login(from_address, "digjid-Dehge9-cambot")
    text = "Subject: CornField email verification\n\nPlease follow this link to verify your email address: https://cornfield.herokuapp.com/verify/" + verification_code
    server.sendmail(from_address, email, text)
    server.quit()
    return {"success": True}