from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
import re
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
from pymongo import MongoClient

client = MongoClient("mongodb+srv://angelgupta:qPkI1uUzKeZern12@eodbplatform.vllgoss.mongodb.net/")

db = client["eodb_users"]  # your custom DB name
users_collection = db["users"]  # Add this line
with open("scrape.json", "r", encoding="utf-8") as f:
    all_schemes = json.load(f)








# Dummy data for approvals
approvals_data = {
    "company_registration": {
        "name": "Company Registration",
        "description": "Register your startup as a Private Limited, LLP, or Proprietorship.",
        "steps": [
            "1. Digital Signature Certificate (DSC) application.",
            "2. Director Identification Number (DIN) application.",
            "3. Name reservation (RUN service) with MCA.",
            "4. SPICe+ form filing for incorporation.",
            "5. E-MoA and E-AoA filing."
        ],
        "portal_link": "https://www.mca.gov.in/content/mca/global/en/home.html",
        "domain_tags": ["general", "all_startups"],
        "estimated_time": "7-10 working days"
    },
    "gst_registration": {
        "name": "GST Registration",
        "description": "Mandatory for businesses with turnover above threshold or for inter-state supply.",
        "steps": [
            "1. Gather required documents (PAN, Aadhaar, Proof of Business Registration, Bank Account details).",
            "2. Visit GST Portal and apply for registration (Form GST REG-01).",
            "3. Complete Aadhar authentication or e-verification.",
            "4. Respond to queries from GST officer (if any).",
            "5. Receive GSTIN."
        ],
        "portal_link": "https://www.gst.gov.in/",
        "domain_tags": ["general", "e-commerce", "retail", "services"],
        "estimated_time": "3-7 working days"
    },
    "msme_udyog_aadhaar": {
        "name": "MSME Udyam Registration",
        "description": "Register as a Micro, Small, or Medium Enterprise to avail government benefits and schemes.",
        "steps": [
            "1. Visit Udyam Registration Portal.",
            "2. Fill in Aadhaar details, PAN, and other business information.",
            "3. No documents or fees required; self-declaration based.",
            "4. Receive Udyam Registration Certificate instantly."
        ],
        "portal_link": "https://udyamregistration.gov.in/",
        "domain_tags": ["general", "all_startups", "subsidies", "schemes"],
        "estimated_time": "1-2 days (online)"
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():
    user_message = request.json.get('message', '').lower()
    response_text = "I'm not sure how to respond to that. Can you ask about 'company registration', 'GST registration', or 'MSME registration'?"
    recommended_approvals = []
    schemes_info = []

    if "hello" in user_message or "hi" in user_message:
        response_text = "Hello! I'm your EODB AI assistant. How can I help you with your startup's approvals or government schemes today? You can ask me about 'company registration', 'GST', or 'MSME registration'."

    elif "company registration" in user_message or "company" in user_message or "register my business" in user_message:
        approval = approvals_data.get("company_registration")
        if approval:
            steps_list = '\n- '.join(approval['steps'])
            response_text = f"""For *{approval['name']}*: {approval['description']}

*Steps:*
- {steps_list}

*Estimated Time:* {approval['estimated_time']}
You can find more details and apply here: {approval['portal_link']}

Is there anything else I can help you with regarding company setup?"""

    elif "gst" in user_message or "gst registration" in user_message:
        approval = approvals_data.get("gst_registration")
        if approval:
            steps_list = '\n- '.join(approval['steps'])
            response_text = f"""Regarding *{approval['name']}*: {approval['description']}

*Steps:*
- {steps_list}

*Estimated Time:* {approval['estimated_time']}
Apply online here: {approval['portal_link']}

Do you need help with other tax registrations?"""

    elif "msme" in user_message or "udyam" in user_message or "msme registration" in user_message or "subsidies" in user_message or "schemes" in user_message:
        approval = approvals_data.get("msme_udyog_aadhaar")
        if approval:
            steps_list = '\n- '.join(approval['steps'])
            response_text = f"""For *{approval['name']}*: {approval['description']}

*Steps:*
- {steps_list}

*Estimated Time:* {approval['estimated_time']}
You can register here: {approval['portal_link']}

This registration can help you access various government schemes and subsidies."""

    elif "domain" in user_message and "startup" in user_message:
        response_text = "What is your startup's domain or industry (e.g., 'FinTech', 'FoodTech', 'E-commerce')? I can provide more specific guidance."

    elif "fintech" in user_message:
        response_text = "For a FinTech startup, beyond general registrations, you'll need specific licenses from RBI, SEBI, or IRDAI depending on your services. I recommend looking into: RBI Payment Bank License, NBFC Registration, or SEBI Investment Advisor Registration. You should also ensure compliance with FEMA and Data Protection laws."
        recommended_approvals = [
            approvals_data.get("company_registration"),
            approvals_data.get("gst_registration")
        ]

    elif "foodtech" in user_message:
        response_text = "If your startup is in FoodTech, you absolutely need an FSSAI Food License. Depending on your operations (manufacturing, distribution, restaurant), the type of license may vary. Also consider: BIS Certification for certain food products."
        recommended_approvals = [
            approvals_data.get("company_registration"),
            approvals_data.get("gst_registration"),
            {"name": "FSSAI Food License", "portal_link": "https://foodlicensing.fssai.gov.in/"}
        ]

    recommended_approvals = [app for app in recommended_approvals if app]

    return jsonify({
        'response': response_text,
        'recommended_approvals': recommended_approvals,
        'schemes_info': schemes_info
    })


@app.route('/find_schemes', methods=['GET'])
def find_schemes():
    return render_template("scheme_form.html")


@app.route('/recommend_schemes', methods=['POST'])
def recommend_schemes():
    idea = request.form.get('startup_idea', '').lower()
    selected_sectors = request.form.getlist('sectors')

    matches = []
    for scheme in all_schemes:
        score = 0
        text_blob = f"{scheme.get('Brief', '')} {scheme.get('Eligibility Criteria', '')} {scheme.get('Key Sector Covered', '')}".lower()

        if idea and any(word in text_blob for word in idea.split()):
            score += 1

        if selected_sectors and any(sector.lower() in text_blob for sector in selected_sectors):
            score += 1

        if score > 0:
            matches.append(scheme)

    return render_template("scheme_results.html", results=matches)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users_collection.find_one({"email": email})
        if user:
            if check_password_hash(user['password'], password):
                session['email'] = user['email']
                return redirect('/')
            else:
                flash("Incorrect password.")
        else:
            flash("Email not found. Please sign up.")
    return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    mname = request.form.get('mname')
    age = int(request.form.get('age'))

    # Validation
    if age < 18:
        flash("You must be 18+ to register.")
        return redirect('/login')

    if password != confirm:
        flash("Passwords do not match.")
        return redirect('/login')

    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
        flash("Password must contain uppercase, lowercase, number, and special character.")
        return redirect('/login')

    if users_collection.find_one({"email": email}):
        flash("Account already exists.")
        return redirect('/login')

    users_collection.insert_one({
        "email": email,
        "password": generate_password_hash(password),
        "fname": fname,
        "lname": lname,
        "mname": mname,
        "age": age
    })
    session['email'] = email
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

    # Debug mode TRUE rakhna development ke liye, production mein FALSE
    # Agar Port 5000 busy ho, toh port=8000 ya koi aur free port use karna
    app.run(debug=True, host='127.0.0.1', port=5001)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
