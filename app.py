from flask import Flask, render_template, request, session, redirect
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, firestore

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Consider using environment variable in production

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login_google", methods=["POST"])
def login_google():
    data = request.get_json()
    id_token = data.get("idToken")
    try:
        # Verify Firebase ID token
        decoded_token = admin_auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email")
        
        # Store in session
        session["user"] = uid
        session["email"] = email

        # Store in Firestore database
        db.collection("users").document(uid).set({
            "email": email
        }, merge=True)  # merge=True avoids overwriting existing fields

        return "OK", 200
    except Exception as e:
        return f"Error: {e}", 400

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", email=session.get("email"))

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)