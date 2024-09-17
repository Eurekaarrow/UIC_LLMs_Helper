from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for
from functools import wraps
from app.models.base import db
from app.models.user import User
from flask_mail import Message
import random
import string

userBP = Blueprint('user', __name__)
#app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_teacher(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if session.get('user_type') != 'teacher':
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_student(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if session.get('user_type') != 'student':
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if session.get('user_type') != 'admin':
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@userBP.route('/send_registration_link', methods=['POST'])
def send_registration_link():
    email = request.form.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'No email provided'}), 400

    code = generate_verification_code()
    message = Message("Your Registration Link", sender="eureka_gyc@163.com", recipients=[email])
    verification_url = url_for('user.register_link', code=code, _external=True)
    message.body = f"Please click the following link to complete your registration: {verification_url}"

    mail = current_app.extensions['mail']
    mail.send(message)

    session['verification_code'] = code
    session['email'] = email

    return jsonify({'status': 'success', 'message': 'Registration link sent'})


@userBP.route('/register_link', methods=['GET'])
def register_link():
    code = request.args.get('code')
    if not code or 'verification_code' not in session or code != session['verification_code']:
        return jsonify({'status': 'error', 'message': 'Invalid or expired registration link'}), 400

    email = session.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Invalid session data'}), 400

    return render_template('register.html', email=email, verification_code=code, verification_mode=True)


@userBP.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', verification_mode=False)
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        verification_code = request.form.get('verification_code')

        if 'verification_code' not in session or verification_code != session['verification_code'] or email != session['email']:
            return jsonify({'status': 'error', 'message': 'Invalid or expired verification code'}), 400

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Please enter both email and password'}), 400

        if '@uic.cn' in email:
            user_type = 'admin'
        elif '@uic.edu.cn' in email:
            user_type = 'teacher'
        elif '@mail.uic.edu.cn' in email or '@mail.uic.edu.hk' in email:
            user_type = 'student'
        else:
            return jsonify({'status': 'error', 'message': 'Invalid email format for this application'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 409

        new_user = User(email=email, password=password, user_type=user_type)  # 密码应该加密
        db.session.add(new_user)
        db.session.commit()

        del session['verification_code']
        del session['email']

        return jsonify({'status': 'success', 'message': f'Registration successful! Welcome, {user_type}.'})


@userBP.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'GET':
        return render_template('login.html', title='Sample Login', header='Sample Case')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Please enter both email and password'}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'status': 'error', 'message': 'No account found with that email'}), 404

        if user.password == password:
            if '@uic.cn' in email:
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_type'] = 'admin'
                return jsonify({'status': 'success', 'redirect_url': url_for('user.admin_homepage')})
            elif '@mail.uic.edu.cn' in email or '@mail.uic.edu.hk' in email:
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_type'] = 'student'
                return jsonify({'status': 'success', 'redirect_url': url_for('user.student_homepage')})
            elif '@uic.edu.cn' in email:
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_type'] = 'teacher'
                return jsonify({'status': 'success', 'redirect_url': url_for('user.teacher_homepage')})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid email format for this application'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Incorrect password'}), 401


@userBP.route('/student_homepage')
@login_required_student
def student_homepage():
    if 'user_email' in session:
        return render_template('StudentHomepage.html', user_email=session['user_email'])
    else:
        return redirect(url_for('user.login'))

@userBP.route('/teacher_homepage')
@login_required_teacher
def teacher_homepage():
    if 'user_email' in session:
        return render_template('Teacher_Homepage.html', user_email=session['user_email'])
    else:
        return redirect(url_for('user.login'))

@userBP.route('/admin_homepage')
@login_required_admin
def admin_homepage():
    if 'user_email' in session:
        return render_template('Admin_Homepage.html', user_email=session['user_email'])
    else:
        return redirect(url_for('user.login'))

@userBP.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))