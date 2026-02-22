from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from services.ai_service import (
    chat_with_ai, analyze_medicine, analyze_disease,
    analyze_report, analyze_image, analyze_symptoms, analyze_emergency
)
from services.ocr_service import extract_text_from_pdf, extract_text_from_image
from services.email_service import send_chat_email
from models.database import save_history, get_user
from config import Config
from datetime import datetime
import requests

bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/chatbot')
def chatbot():
    if 'user_mobile' not in session:
        return redirect(url_for('auth.login'))

    return render_template('chat.html',
                           languages=Config.LANGUAGES,
                           categories=Config.CATEGORIES,
                           user_name=session.get('user_name'))


@bp.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    category = data.get('category', 'general')
    language = data.get('language', 'English')
    mobile = session.get('user_mobile')

    if category == 'general':
        message = data.get('message')
        response = chat_with_ai(message, language)

        save_history(mobile, 'chat', {
            "question": message,
            "response": response,
            "language": language,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({"success": True, "response": response})

    elif category == 'medicine':
        search_term = data.get('search_term')
        mode = data.get('mode', 'Medicine Based')

        if mode == 'Disease Based':
            response = analyze_disease(search_term, language)
        else:
            response = analyze_medicine(search_term, language)

        save_history(mobile, 'medicine', {
            "search_type": mode,
            "search_term": search_term,
            "language": language,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({"success": True, "response": response})

    elif category == 'symptoms':
        symptoms = data.get('symptoms')
        age = data.get('age')
        gender = data.get('gender')
        duration = data.get('duration')
        severity = data.get('severity')

        response = analyze_symptoms(symptoms, age, gender, duration, severity, language)

        save_history(mobile, 'symptom', {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "duration": duration,
            "severity": severity,
            "language": language,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({"success": True, "response": response})

    elif category == 'emergency':
        emergency_desc = data.get('emergency_desc')
        level = data.get('level')
        vital_signs = data.get('vital_signs', '')

        response = analyze_emergency(emergency_desc, level, vital_signs, language)

        if level == "Critical":
            response = "🚨 <b>CRITICAL EMERGENCY - CALL 108 IMMEDIATELY!</b><br><br>" + response

        save_history(mobile, 'emergency', {
            "emergency_desc": emergency_desc,
            "level": level,
            "vital_signs": vital_signs,
            "language": language,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({"success": True, "response": response})

    return jsonify({"success": False, "message": "Unknown category"}), 400


@bp.route('/upload-file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    file_type = request.form.get('file_type')
    language = request.form.get('language', 'English')
    mobile = session.get('user_mobile')

    if file_type == 'PDF Report':
        extracted_text = extract_text_from_pdf(file)
        if not extracted_text.startswith("Error"):
            response = analyze_report(extracted_text, language)
        else:
            response = extracted_text
    else:
        extracted_text = extract_text_from_image(file)
        if not extracted_text.startswith("Error"):
            response = analyze_image(extracted_text, language)
        else:
            response = extracted_text

    save_history(mobile, 'report', {
        "filename": file.filename,
        "type": file_type,
        "language": language,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"success": True, "response": response})


@bp.route('/find-hospitals', methods=['POST'])
def find_hospitals():
    data = request.get_json()
    district = data.get('district')
    state = data.get('state', '')

    locality = f"{district} district"
    if state:
        locality += f", {state}"

    try:
        geocode_url = f"https://api.geoapify.com/v1/geocode/search?text={locality}&limit=1&apiKey={Config.GEOAPIFY_API_KEY}"
        geo_resp = requests.get(geocode_url, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data.get("features"):
            return jsonify({"success": False, "message": "Location not found"}), 404

        lon, lat = geo_data["features"][0]["geometry"]["coordinates"]

        places_url = f"https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:{lon},{lat},30000&limit=15&apiKey={Config.GEOAPIFY_API_KEY}"
        resp = requests.get(places_url, timeout=10)
        places = resp.json().get("features", [])

        hospitals = []
        for place in places:
            props = place["properties"]
            hospitals.append({
                "name": props.get("name", "Unknown Hospital"),
                "address": props.get("address_line1", "N/A"),
                "district": props.get("state_district") or props.get("city") or district,
                "state": props.get("state", state or "N/A"),
                "postal_code": props.get("postcode", "N/A"),
                "google_maps": f"https://www.google.com/maps/search/{props.get('name', '').replace(' ', '+')}"
            })

        return jsonify({"success": True, "hospitals": hospitals})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    email = data.get('email')
    chat_messages = data.get('chat_messages', [])
    user_name = session.get('user_name')

    success, message = send_chat_email(email, user_name, chat_messages)

    return jsonify({"success": success, "message": message})