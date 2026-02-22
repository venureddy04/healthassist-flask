from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from models.database import get_user_history, delete_history_item, clear_user_history, get_history_item
from services.email_service import send_history_item_email

bp = Blueprint('history', __name__, url_prefix='/history')


@bp.route('/')
def view_history():
    if 'user_mobile' not in session:
        return redirect(url_for('auth.login'))

    mobile = session.get('user_mobile')
    history = get_user_history(mobile)

    return render_template('history.html', history=history)


@bp.route('/delete/<int:history_id>', methods=['POST'])
def delete_item(history_id):
    delete_history_item(history_id)
    return jsonify({"success": True, "message": "History item deleted"})


@bp.route('/clear', methods=['POST'])
def clear_history():
    mobile = session.get('user_mobile')
    clear_user_history(mobile)
    return jsonify({"success": True, "message": "History cleared"})


@bp.route('/send-item-email/<int:history_id>', methods=['POST'])
def send_item_email(history_id):
    """Send a single history item as PDF to provided email"""
    if 'user_mobile' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json()
    recipient_email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not recipient_email:
        return jsonify({"success": False, "message": "Email address is required"}), 400

    # Basic email validation
    if '@' not in recipient_email or '.' not in recipient_email:
        return jsonify({"success": False, "message": "Invalid email address"}), 400

    history_item = get_history_item(history_id)
    if not history_item:
        return jsonify({"success": False, "message": "History item not found"}), 404

    user_name = session.get('user_name', 'User')

    success, message = send_history_item_email(
        recipient_email,
        user_name,
        history_item,
        subject,
        body
    )

    return jsonify({"success": success, "message": message})