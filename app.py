from flask import Flask, render_template, session, redirect, url_for
from flask_mail import Mail
from config import Config
from routes import auth, chat, history
from models.database import init_supabase

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize extensions
mail = Mail(app)
init_supabase()

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(chat.bp)
app.register_blueprint(history.bp)

@app.route('/')
def landing():
    """Landing page with falling flowers animation"""
    return render_template('landing.html')
@app.route('/home')
def home():
    if 'user_mobile' in session:
        return redirect(url_for('chat.chatbot'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run()