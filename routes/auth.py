from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from models.database import create_user, verify_login, get_user, update_password, set_security_question, verify_security_answer

bp = Blueprint('auth', __name__, url_prefix='/auth')

SECURITY_QUESTIONS = [
    "What is your mother's maiden name?",
    "What city were you born in?",
    "What is your favorite food?",
    "What is your pet's name?",
    "What is your favorite color?"
]

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        mobile = data.get('mobile', '')
        password = data.get('password', '')

        if len(mobile) != 10 or not mobile.isdigit():
            return jsonify({"success": False, "message": "Invalid mobile number"}), 400

        success, message = verify_login(mobile, password)

        if success:
            session['user_mobile'] = mobile
            user = get_user(mobile)
            session['user_name'] = user['name']
            return jsonify({"success": True, "redirect": url_for('chat.chatbot')})

        return jsonify({"success": False, "message": message}), 401

    return render_template('auth.html', security_questions=SECURITY_QUESTIONS)

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name', '')
    mobile = data.get('mobile', '')
    password = data.get('password', '')
    security_question = data.get('security_question', '')
    security_answer = data.get('security_answer', '')

    if not name or len(mobile) != 10 or not mobile.isdigit() or len(password) < 6:
        return jsonify({"success": False, "message": "Invalid input"}), 400

    success, message = create_user(mobile, name, password)

    if success:
        set_security_question(mobile, security_question, security_answer)
        return jsonify({"success": True, "message": "Account created! Please login."})

    return jsonify({"success": False, "message": message}), 400

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    step = data.get('step')

    if step == 'verify_mobile':
        mobile = data.get('mobile', '')
        user = get_user(mobile)

        if user and user.get('security_question'):
            return jsonify({
                "success": True,
                "security_question": user['security_question']
            })
        return jsonify({"success": False, "message": "Mobile not registered"}), 404

    elif step == 'verify_answer':
        mobile = data.get('mobile', '')
        answer = data.get('answer', '')

        success, message = verify_security_answer(mobile, answer)
        return jsonify({"success": success, "message": message})

    elif step == 'reset_password':
        mobile = data.get('mobile', '')
        new_password = data.get('new_password', '')

        success, message = update_password(mobile, new_password)
        return jsonify({"success": success, "message": message})

    return jsonify({"success": False, "message": "Invalid step"}), 400

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))