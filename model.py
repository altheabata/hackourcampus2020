from passlib.hash import sha256_crypt

def attempt_login(email, password, mongo):
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