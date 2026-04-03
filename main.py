from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.secret_key = "super-secret-key-change-this"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@app.route('/')
def index():
    if 'uid' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')  # Your login page

@app.route('/login_google', methods=['POST'])
def login_google():
    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({'error': 'No ID token provided'}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')

        session.permanent = True
        session['uid'] = uid
        session['email'] = email

        return jsonify({'message': 'Login successful!', 'uid': uid})

    except Exception as e:
        return jsonify({'error': f'Invalid token: {str(e)}'}), 400

@app.route('/dashboard')
def dashboard():
    if 'uid' not in session:
        return redirect(url_for('index'))
    # Pass user info to the dashboard template
    return render_template('dashboard.html', email=session.get('email'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
