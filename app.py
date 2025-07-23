from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dummy data for approvals (normally this would come from a database or external JSON)
# Abhi ke liye ye simple Python dictionary use kar rahe hain.
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
    },
    # Add more approvals as needed for your prototype
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
            # FIXED: Changed to triple-quoted f-string for multi-line content
            response_text = f"""For **{approval['name']}**: {approval['description']}

**Steps:**
- {'\n- '.join(approval['steps'])}

**Estimated Time:** {approval['estimated_time']}
You can find more details and apply here: {approval['portal_link']}

Is there anything else I can help you with regarding company setup?"""
    elif "gst" in user_message or "gst registration" in user_message:
        approval = approvals_data.get("gst_registration")
        if approval:
            # FIXED: Changed to triple-quoted f-string for multi-line content
            response_text = f"""Regarding **{approval['name']}**: {approval['description']}

**Steps:**
- {'\n- '.join(approval['steps'])}

**Estimated Time:** {approval['estimated_time']}
Apply online here: {approval['portal_link']}

Do you need help with other tax registrations?"""
    elif "msme" in user_message or "udyam" in user_message or "msme registration" in user_message or "subsidies" in user_message or "schemes" in user_message:
        approval = approvals_data.get("msme_udyog_aadhaar")
        if approval:
            # FIXED: Changed to triple-quoted f-string for multi-line content
            response_text = f"""For **{approval['name']}**: {approval['description']}

**Steps:**
- {'\n- '.join(approval['steps'])}

**Estimated Time:** {approval['estimated_time']}
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
            {"name": "FSSAI Food License", "portal_link": "https://foodlicensing.fssai.gov.in/"} # Dummy for now if not in approvals_data
        ]
    
    # Filter out None values from recommended_approvals if some keys not found
    recommended_approvals = [app for app in recommended_approvals if app]


    return jsonify({
        'response': response_text,
        'recommended_approvals': recommended_approvals,
        'schemes_info': schemes_info # Currently empty, but can be filled by an ML model later
    })

if __name__ == '__main__':
    # Debug mode TRUE rakhna development ke liye, production mein FALSE
    # Agar Port 5000 busy ho, toh port=8000 ya koi aur free port use karna
    app.run(debug=True, host='0.0.0.0', port=5001)