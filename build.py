import os

structure = {
    'requirements.txt': '''Flask==3.0.0
pymongo==4.6.0
Flask-PyMongo==2.3.0
Werkzeug==3.0.1
python-dotenv==1.0.0''',
    
    'app.py': '''from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'department_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

client = MongoClient('mongodb://localhost:27017/')
db = client['department_db']

users_col = db['users']
notes_col = db['notes']
news_col = db['news']
achievements_col = db['achievements']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorator
    return decorator

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def utility_processor():
    recent_news = list(news_col.find().sort("date", -1).limit(3))
    marquee_text = " | ".join([n['title'] for n in recent_news]) if recent_news else "Welcome to the Department Portal! Latest updates and announcements will appear here."
    return dict(marquee_text=marquee_text)

@app.route('/')
def index():
    recent_achievements = list(achievements_col.find().sort("date", -1).limit(3))
    return render_template('index.html', achievements=recent_achievements)

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/faculty')
def faculty():
    faculties = list(users_col.find({'role': 'faculty', 'approved': True}))
    return render_template('faculty.html', faculties=faculties)

@app.route('/achievements')
def achievements():
    achievements_list = list(achievements_col.find().sort("date", -1))
    return render_template('achievements.html', achievements=achievements_list)

@app.route('/news')
def news():
    news_list = list(news_col.find().sort("date", -1))
    return render_template('news.html', news=news_list)

@app.route('/notes')
def notes():
    search_query = request.args.get('q', '')
    if search_query:
        notes_list = list(notes_col.find({"title": {"$regex": search_query, "$options": "i"}}))
    else:
        notes_list = list(notes_col.find())
    return render_template('notes.html', notes=notes_list, search_query=search_query)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users_col.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            if not user.get('approved', False):
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        if users_col.find_one({'email': email}):
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        is_first_user = users_col.count_documents({}) == 0
        approved = True if is_first_user else False
        user_role = 'admin' if is_first_user else role

        user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': user_role,
            'approved': approved,
            'created_at': datetime.utcnow()
        }
        users_col.insert_one(user)
        flash('Registration successful. Please wait for admin approval.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    pending_users = list(users_col.find({'approved': False}))
    all_users = list(users_col.find())
    return render_template('dashboard/admin.html', pending_users=pending_users, users=all_users)

@app.route('/dashboard/faculty')
@login_required
@role_required('faculty')
def faculty_dashboard():
    my_notes = list(notes_col.find({'uploaded_by': session['user_name']}))
    return render_template('dashboard/faculty.html', notes=my_notes)

@app.route('/dashboard/student')
@login_required
@role_required('student')
def student_dashboard():
    return render_template('dashboard/student.html')

@app.route('/admin/approve/<user_id>')
@login_required
@role_required('admin')
def approve_user(user_id):
    users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'approved': True}})
    flash('User approved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    users_col.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/faculty/upload_note', methods=['POST'])
@login_required
@role_required('faculty')
def upload_note():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('faculty_dashboard'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('faculty_dashboard'))
    if file:
        filename = file.filename
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        note = {
            'title': request.form.get('title'),
            'subject': request.form.get('subject'),
            'filename': filename,
            'filepath': filepath,
            'uploaded_by': session['user_name'],
            'date': datetime.utcnow()
        }
        notes_col.insert_one(note)
        flash('Note uploaded successfully.', 'success')
    return redirect(url_for('faculty_dashboard'))

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True, port=5000)
'''
}

for filepath, content in structure.items():
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Setup Complete")
