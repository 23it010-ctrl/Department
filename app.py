from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify # type: ignore
from pymongo import MongoClient # type: ignore
import os
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from functools import wraps
from datetime import datetime
from bson.objectid import ObjectId # type: ignore

# ── New Service Imports (Modular Architecture) ───────────────────────────────
from services.validation_engine import validate_submission
from services.voting_engine import cast_vote, get_vote_tally, evaluate_votes
from services.rate_limiter import check_rate_limit, record_submission


# Default Site Settings
DEFAULT_SETTINGS = {
    "site_id": "main_config",
    "theme": "light",
    "header_title": {"en": "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", "ta": "கணினி அறிவியல் மற்றும் பொறியியல் துறை"},
    "header_subtitle": {"en": "Excellence in Technology", "ta": "தொழில்நுட்பத்தில் சிறந்து விளங்குதல்"},
    "college_name": {"en": "INDIAN INSTITUTE OF TECHNOLOGY NATIONAL (IITN)", "ta": "இந்திய தொழில்நுட்ப நிறுவனம் தேசிய (IITN)"},
    "left_logo": "dept_logo_left.png",
    "right_logo": "dept_logo_right.png",
    "hero_bg": "campus_hero_bg.png",
    "hero_title": {"en": "Welcome to the Department Portal", "ta": "துறை போர்ட்டலுக்கு உங்களை வரவேற்கிறோம்"},
    "hero_description": {"en": "Empowering students through innovation, research, and world-class education.", "ta": "கண்டுபிடிப்பு, ஆராய்ச்சி மற்றும் உலகத்தரம் வாய்ந்த கல்வி மூலம் மாணவர்களுக்கு அதிகாரம் அளித்தல்."},
    "nav_items": [
        {"label": {"en": "HOME", "ta": "முகப்பு"}, "url": "/"},
        {"label": {"en": "STUDENTS", "ta": "மாணவர்கள்"}, "url": "/students"},
        {"label": {"en": "FACULTY", "ta": "ஆசிரியர்கள்"}, "url": "/faculty"},
        {"label": {"en": "ACHIEVEMENTS", "ta": "சாதனைகள்"}, "url": "/achievements"},
        {"label": {"en": "NEWS", "ta": "செய்திகள்"}, "url": "/news"},
        {"label": {"en": "NOTES", "ta": "குறிப்புகள்"}, "url": "/notes"},
        {"label": {"en": "SUBMIT CONTENT", "ta": "உள்ளடக்கத்தைச் சமர்ப்பிக்கவும்"}, "url": "/submit-content"},
        {"label": {"en": "COMMUNITY REVIEW", "ta": "சமூக மதிப்பாய்வு"}, "url": "/pending-content"},
        {"label": {"en": "CONTACT", "ta": "தொடர்பு"}, "url": "/contact"}
    ],
    "contact_address": "Department of CSE, IITN Campus, Tech Road, City, State, 100001",
    "contact_phone": "+91 123 456 7890",
    "contact_email": "info@cse.iitn.ac.in",
    "contact_location": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15545.9123456789!2d80.2312!3d12.9915!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTLCsDU5JzI5LjQiTiA4MMKwMTMnNTIuMyJF!5e0!3m2!1sen!2sin!4v1234567890123"
}

app = Flask(__name__)
app.secret_key = 'department_secret_key_2026'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# ── Ensure Required Directories Exist (Crucial for Cloud Deployment) ──────────
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'images'), exist_ok=True)

# ── Built-in Admin (works even without MongoDB) ──────────────────────────────
BUILTIN_ADMIN = {
    '_id': 'builtin_admin',
    'name': 'Admin',
    'email': 'admin@dept.com',
    'password': generate_password_hash('Admin@1234'),
    'role': 'admin',
    'approved': True
}

# MongoDB Connection
# Priority: 1. Environment Variable (Vercel/Atlas) -> 2. Localhost -> 3. JSON Fallback
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')

client = None
db = None
try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=3000)
    # Check if connection is alive
    client.server_info()
    db = client['department_db']
    print(f"[OK] Connected to MongoDB via {mongodb_uri}")
except Exception as e:
    print(f"[WARNING] MongoDB connection failed: {e}. Falling back to JSON/Mock mode.")
    client = None
    db = None

import json

class JSONCursor:
    def __init__(self, data): self.data = data
    def sort(self, key, direction):
        if self.data and isinstance(self.data[0], dict) and key in self.data[0]:
            self.data.sort(key=lambda x: str(x.get(key, '')), reverse=(direction == -1))
        return self
    def limit(self, n):
        self.data = self.data[:n]
        return self
    def __iter__(self): return iter(self.data)
    def __len__(self): return len(self.data)

class JSONCollection:
    def __init__(self, name):
        self.filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}.json")
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
    def _read(self):
        if not os.path.exists(self.filename): return []
        try:
            with open(self.filename, 'r') as f: return json.load(f)
        except: return []
    def _write(self, data):
        with open(self.filename, 'w') as f: json.dump(data, f, indent=4)
    def _match(self, q, doc):
        for k, v in q.items():
            if isinstance(v, dict) and '$ne' in v:
                ne_val = v.get('$ne')
                if str(doc.get(k)) == str(ne_val): return False
            elif str(doc.get(k)) != str(v): return False
        return True
    def find(self, query=None):
        data = self._read()
        if not query: return JSONCursor(data)
        return JSONCursor([d for d in data if self._match(query, d)])
    def find_one(self, query):
        res = self.find(query)
        return res.data[0] if res.data else None
    def insert_one(self, doc):
        doc['_id'] = os.urandom(12).hex()
        for k, v in doc.items():
            if isinstance(v, datetime): doc[k] = v.isoformat()
        data = self._read()
        data.append(doc)
        self._write(data)
    def update_one(self, query, update, upsert=False):
        data = self._read()
        found = False
        for i, doc in enumerate(data): # type: ignore
            if self._match(query, doc):
                for k, v in update.get('$set', {}).items(): # type: ignore
                    data[i][k] = v
                found = True
                break
        if not found and upsert:
            new_doc = query.copy()
            new_doc.update(update.get('$set', {}))
            new_doc['_id'] = os.urandom(12).hex()
            data.append(new_doc) # type: ignore
        self._write(data)
    def delete_one(self, query):
        data = self._read()
        new_data = [d for d in data if not self._match(query, d)]
        self._write(new_data)
    def count_documents(self, query):
        return len(self.find(query).data)

def get_col(name):
    if db is not None:
        return db[name]
    return JSONCollection(name)

# ── Decorators ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('user_role') != role:
                flash('Access denied.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Context Processors ───────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    try:
        # Site Settings
        settings_col = get_col('settings')
        site_settings = DEFAULT_SETTINGS.copy()
        
        if settings_col is not None:
            saved = settings_col.find_one({"site_id": "main_config"})
            if saved:
                # Merge saved settings into defaults
                for k, v in saved.items():
                    site_settings[k] = v
        
        # ── UNIVERSAL BILINGUAL HEALER ──────────────────────────────────────────
        # Ensure all required bilingual fields are properly formatted as dicts.
        # This prevents 500 errors if OLD non-bilingual data exists in the DB.
        bilingual_fields = [
            'header_title', 'header_subtitle', 'college_name', 
            'hero_title', 'hero_description'
        ]
        
        for field in bilingual_fields:
            val = site_settings.get(field)
            if val and isinstance(val, str):
                # Auto-upgrade: Convert string to dict with same value for both
                site_settings[field] = {"en": val, "ta": val}
            elif not val or not isinstance(val, dict):
                # Fallback to default if missing or invalid
                site_settings[field] = DEFAULT_SETTINGS.get(field, {"en": "Portal", "ta": "Portal"})

        # HEAL navigation items: Ensure all have bilingual labels
        if 'nav_items' in site_settings:
            fixed_nav = []
            for item in site_settings['nav_items']:
                label = item.get('label', 'Menu')
                if isinstance(label, str):
                    item['label'] = {'en': label, 'ta': label}
                elif not isinstance(label, dict):
                    item['label'] = {'en': str(label), 'ta': str(label)}
                fixed_nav.append(item)
            site_settings['nav_items'] = fixed_nav

        # Language & Theme
        lang = session.get('lang', 'en')
        theme = session.get('theme', site_settings.get('theme', 'light'))
        
        # Marquee
        marquee_text = "Welcome! | Semester Registration Open | News Updates"
        news_col = get_col('news')
        if news_col is not None:
            try:
                recent = list(news_col.find().sort("date", -1).limit(5))
                if recent:
                    marquee_text = " | ".join([str(n.get('title', 'Update')) for n in recent])
            except:
                pass

        # Current User
        current_user = None
        if 'user_id' in session:
            user_id = session.get('user_id')
            if user_id:
                users_col = get_col('users')
                if users_col is not None:
                    try:
                        current_user = users_col.find_one({'_id': ObjectId(user_id)})
                        if not current_user:
                            current_user = users_col.find_one({'_id': user_id})
                    except:
                        current_user = users_col.find_one({'_id': user_id})
        
        return {
            'marquee_text': marquee_text, 
            'now': datetime.utcnow(), 
            'site': site_settings, 
            'lang': lang, 
            'theme': theme, 
            'user': current_user
        }
    except Exception as e:
        # Fallback to absolute minimum to prevent 500 on every page
        print(f"CRITICAL ERROR in inject_globals: {str(e)}")
        return {
            'marquee_text': "Welcome", 
            'now': datetime.utcnow(), 
            'site': DEFAULT_SETTINGS, 
            'lang': 'en', 
            'theme': 'light', 
            'user': None
        }

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['en', 'ta']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/set_theme/<theme>')
def set_theme(theme):
    if theme in ['light', 'dark']:
        session['theme'] = theme
    return redirect(request.referrer or url_for('index'))

# ── Public Routes ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    achievements = []
    col = get_col('achievements')
    if col is not None:
        achievements = list(col.find().sort("date", -1).limit(3))
    return render_template('index.html', achievements=achievements)

@app.route('/students')
def students():
    students_list = []
    col = get_col('users')
    if col is not None:
        students_list = list(col.find({'role': 'student', 'approved': True}))
    return render_template('students.html', students=students_list)

@app.route('/faculty')
def faculty():
    faculties = []
    col = get_col('users')
    if col is not None:
        faculties = list(col.find({'role': 'faculty', 'approved': True}))
    return render_template('faculty.html', faculties=faculties)

@app.route('/achievements')
def achievements():
    achievements_list = []
    col = get_col('achievements')
    if col is not None:
        achievements_list = list(col.find().sort("date", -1))
    return render_template('achievements.html', achievements=achievements_list)

@app.route('/news')
def news():
    news_list = []
    col = get_col('news')
    if col is not None:
        news_list = list(col.find().sort("date", -1))
    return render_template('news.html', news=news_list)

@app.route('/notes')
def notes():
    search_query = request.args.get('q', '').strip()
    notes_list = []
    col = get_col('notes')
    if col is not None:
        query = {"title": {"$regex": search_query, "$options": "i"}} if search_query else {}
        notes_list = list(col.find(query).sort("date", -1))
    return render_template('notes.html', notes=notes_list, search_query=search_query)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Check built-in admin first (always works, no MongoDB needed)
        user = None
        if email == BUILTIN_ADMIN['email'] and check_password_hash(BUILTIN_ADMIN['password'], password):
            user = BUILTIN_ADMIN
        else:
            col = get_col('users')
            if col is not None:
                user = col.find_one({'email': email})
                if user and not check_password_hash(user['password'], password):
                    user = None

        if user:
            # Role Check
            login_role = str(request.form.get('login_role', 'student'))
            user_role = str(user.get('role', 'student'))
            if login_role and user_role != 'admin' and user_role != login_role:
                flash(f"Access Denied: You are trying to log in as {login_role.capitalize()}, but your account is registered as a {user_role.capitalize()}.", 'danger')
                return redirect(url_for('login'))

            # Check explicit rejection or pending status
            status = user.get('status', 'approved' if user.get('approved') else 'pending')
            
            if status == 'rejected':
                flash('Your registration was rejected by the admin. You cannot access the site.', 'danger')
                return redirect(url_for('login'))
            elif status == 'pending':
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            if user['role'] != 'admin':
                flash(f'You are now approved and can use this website. Welcome {user["name"]}!', 'success')
            else:
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
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        roll_no = request.form.get('roll_no', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', 'First Year').strip()

        # Handle photo upload
        photo_filename = 'default_avatar.png'
        file = request.files.get('photo')
        if file and file.filename != '':
            photo_filename = file.filename
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, photo_filename))

        col = get_col('users')
        if col.find_one({'email': email}):
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        user = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'roll_no': roll_no,
            'department': department or 'Computer Science',
            'year': year,
            'photo': photo_filename,
            'approved': False,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        col.insert_one(user)
        flash('Registration submitted successfully. A notification has been sent to the admin. Please await admin approval.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ── Dashboards ────────────────────────────────────────────────────────────────
@app.route('/dashboard/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    col = get_col('users')
    pending_users = list(col.find({'approved': {'$ne': True}})) if col is not None else []
    all_users = list(col.find()) if col is not None else []
    
    news_col = get_col('news')
    all_news = list(news_col.find().sort("date", -1)) if news_col is not None else []

    # Fetch pending content submissions for the Content Review tab
    submissions_col = get_col('submitted_content')
    pending_submissions = list(submissions_col.find({'status': 'pending'})) if submissions_col is not None else []
    
    return render_template('dashboard/admin.html',
                           pending_users=pending_users,
                           users=all_users,
                           news_list=all_news,
                           pending_submissions=pending_submissions)

@app.route('/dashboard/faculty')
@login_required
@role_required('faculty')
def faculty_dashboard():
    col = get_col('notes')
    my_notes = list(col.find({'uploaded_by': session['user_name']}).sort("date", -1)) if col is not None else []
    
    # Fetch current faculty user for profile form
    user = {}
    users_col = get_col('users')
    if users_col is not None:
        user_id_str = session['user_id']
        try:
            user = users_col.find_one({'_id': ObjectId(user_id_str)}) or users_col.find_one({'_id': user_id_str}) or {}
        except:
            user = users_col.find_one({'_id': user_id_str}) or {}
    
    return render_template('dashboard/faculty.html', notes=my_notes, user=user)

@app.route('/dashboard/student')
@login_required
@role_required('student')
def student_dashboard():
    col = get_col('users')
    user = {}
    if col is not None:
        # Try finding with ObjectId, fallback to string for JSON db
        user_id_str = session['user_id']
        try:
            user = col.find_one({'_id': ObjectId(user_id_str)}) or col.find_one({'_id': user_id_str})
        except:
            user = col.find_one({'_id': user_id_str})
    return render_template('dashboard/student.html', user=user)

@app.route('/dashboard/student/profile', methods=['POST'])
@login_required
@role_required('student')
def update_student_profile():
    col = get_col('users')
    if col is not None:
        update_data = {
            'name': request.form.get('name'),
            'roll_no': request.form.get('roll_no'),
            'department': request.form.get('department'),
            'mobile': request.form.get('mobile'),
            'email': request.form.get('email'),
            'age': request.form.get('age')
        }
        
        user_id_str = session['user_id']
        try:
            query = {'_id': ObjectId(user_id_str)}
            if not col.find_one(query):
                query = {'_id': user_id_str}
        except:
            query = {'_id': user_id_str}
            
        col.update_one(query, {'$set': update_data})
        session['user_name'] = request.form.get('name')
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/update_faculty_profile', methods=['POST'])
@login_required
@role_required('faculty')
def update_faculty_profile():
    col = get_col('users')
    if col is not None:
        update_data = {
            'name': request.form.get('name'),
            'faculty_id': request.form.get('faculty_id'),
            'faculty_role': request.form.get('faculty_role'),
            'email': request.form.get('email'),
            'age': request.form.get('age')
        }
        
        user_id_str = session['user_id']
        try:
            query = {'_id': ObjectId(user_id_str)}
            if not col.find_one(query):
                query = {'_id': user_id_str}
        except:
            query = {'_id': user_id_str}
            
        col.update_one(query, {'$set': update_data})
        session['user_name'] = request.form.get('name')
        flash('Faculty profile updated successfully!', 'success')
    return redirect(url_for('faculty_dashboard'))

# ── News Actions (Admin) ───────────────────────────────────────────────────────
@app.route('/news/add', methods=['POST'])
@login_required
@role_required('admin')
def add_news():
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'General')
    
    photo_filename = None
    file = request.files.get('image')
    if file and file.filename != '':
        photo_filename = file.filename
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, photo_filename))
    
    col = get_col('news')
    if col is not None:
        col.insert_one({
            'title': title,
            'content': content,
            'category': category,
            'image': photo_filename,
            'date': datetime.now().strftime('%b %d, %Y')
        })
    flash('News published successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/news/delete/<news_id>')
@login_required
@role_required('admin')
def delete_news(news_id):
    col = get_col('news')
    if col is not None:
        try:
            col.delete_one({'_id': ObjectId(news_id)})
        except Exception:
            col.delete_one({'_id': news_id})
    flash('News deleted.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/news/update', methods=['POST'])
@login_required
@role_required('admin')
def update_news():
    news_id = request.form.get('news_id')
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category')
    
    update_data = {
        'title': title,
        'content': content,
        'category': category
    }
    
    file = request.files.get('image')
    if file and file.filename != '':
        photo_filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        update_data['image'] = photo_filename
        
    col = get_col('news')
    if col is not None:
        try:
            col.update_one({'_id': ObjectId(news_id)}, {'$set': update_data})
        except Exception:
            col.update_one({'_id': news_id}, {'$set': update_data})
    flash('News updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ── Admin Actions ─────────────────────────────────────────────────────────────
@app.route('/admin/approve/<user_id>')
@login_required
@role_required('admin')
def approve_user(user_id):
    col = get_col('users')
    if col is not None:
        try:
            col.update_one({'_id': ObjectId(user_id)}, {'$set': {'approved': True, 'status': 'approved'}})
        except Exception:
            col.update_one({'_id': user_id}, {'$set': {'approved': True, 'status': 'approved'}})
    flash('User approved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<user_id>')
@login_required
@role_required('admin')
def reject_user(user_id):
    col = get_col('users')
    if col is not None:
        try:
            col.update_one({'_id': ObjectId(user_id)}, {'$set': {'approved': False, 'status': 'rejected'}})
        except Exception:
            col.update_one({'_id': user_id}, {'$set': {'approved': False, 'status': 'rejected'}})
    flash('User has been rejected.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    col = get_col('users')
    if col is not None:
        try:
            col.delete_one({'_id': ObjectId(user_id)})
        except Exception:
            col.delete_one({'_id': user_id})
    flash('User removed permanently.', 'success')
    return redirect(url_for('admin_dashboard'))

# ── Faculty Actions ───────────────────────────────────────────────────────────
@app.route('/faculty/upload_note', methods=['POST'])
@login_required
@role_required('faculty')
def upload_note():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('Please select a file to upload.', 'danger')
        return redirect(url_for('faculty_dashboard'))

    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filename = file.filename
    file.save(os.path.join(upload_dir, filename))

    col = get_col('notes')
    if col is not None:
        col.insert_one({
            'title': request.form.get('title', filename),
            'subject': request.form.get('subject', 'General'),
            'filename': filename,
            'uploaded_by': session['user_name'],
            'date': datetime.utcnow()
        })
    flash('Note uploaded successfully!', 'success')
    return redirect(url_for('faculty_dashboard'))

@app.route('/achievements/upload', methods=['POST'])
@login_required
def upload_achievement():
    if session.get('user_role') != 'student':
        flash('Only students can upload certificates.', 'danger')
        return redirect(url_for('achievements'))
        
    file = request.files.get('certificate')
    if not file or file.filename == '':
        flash('Please select a certificate image to upload.', 'danger')
        return redirect(url_for('achievements'))

    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filename = file.filename
    file.save(os.path.join(upload_dir, filename))

    col = get_col('achievements')
    if col is not None:
        col.insert_one({
            'title': request.form.get('title', 'Student Certificate'),
            'description': request.form.get('description', 'A certificate uploaded by a student.'),
            'image': filename,
            'uploaded_by': session['user_name'],
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        })
    flash('Certificate uploaded successfully!', 'success')
    return redirect(url_for('achievements'))

# ── Admin Site Settings ──────────────────────────────────────────────────────
@app.route('/admin/update_settings', methods=['POST'])
@login_required
@role_required('admin')
def update_settings():
    col = get_col('settings')
    if col is None:
        flash('Database not available.', 'danger')
        return redirect(url_for('admin_dashboard'))

    new_settings = {
        "header_title": {
            "en": request.form.get('header_title_en'),
            "ta": request.form.get('header_title_ta')
        },
        "header_subtitle": {
            "en": request.form.get('header_subtitle_en'),
            "ta": request.form.get('header_subtitle_ta')
        },
        "college_name": {
            "en": request.form.get('college_name_en'),
            "ta": request.form.get('college_name_ta')
        },
        "hero_title": {
            "en": request.form.get('hero_title_en'),
            "ta": request.form.get('hero_title_ta')
        },
        "hero_description": {
            "en": request.form.get('hero_description_en'),
            "ta": request.form.get('hero_description_ta')
        },
        "contact_address": request.form.get('contact_address'),
        "contact_phone": request.form.get('contact_phone'),
        "contact_email": request.form.get('contact_email'),
        "contact_location": request.form.get('contact_location')
    }

    # Handle Navbar items
    new_nav = []
    for i in range(10): # support up to 10 items
        label_en = request.form.get(f'nav_label_en_{i}')
        if label_en:
            new_nav.append({
                "label": {
                    "en": label_en,
                    "ta": request.form.get(f'nav_label_ta_{i}')
                },
                "url": request.form.get(f'nav_url_{i}')
            })
    if new_nav:
        new_settings["nav_items"] = new_nav # type: ignore

    # Handle file uploads for logos/bg
    for field in ['left_logo', 'right_logo', 'hero_bg']:
        file = request.files.get(field)
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join('static', 'images', filename))
            new_settings[field] = filename

    col.update_one({"site_id": "main_config"}, {"$set": new_settings}, upsert=True) # type: ignore
    flash('Site settings updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# ══════════════════════════════════════════════════════════════════════════════
#  NEW MODULE: Content Submission & Validation Pipeline
# ══════════════════════════════════════════════════════════════════════════════

# ── /submit-content → Show form (GET) or process submission (POST) ───────────
@app.route('/submit-content', methods=['GET', 'POST'])
@login_required
def submit_content():
    """
    GET: Show the content submission form.
    POST: Submit content through the auto-validation engine.
    Content is NOT published directly — it goes through
    ML analysis, API checks, and quality scoring first.
    
    Based on confidence score:
      >= 80 → Auto-approved and published
      50-79 → Sent to community voting
      < 50  → Rejected (spam/low quality)
    """
    # ── GET: Show the submission form ────────────────────────────────────
    if request.method == 'GET':
        return render_template('submit_content.html')

    # ── POST: Process the submission ─────────────────────────────────────
    user_id = session.get('user_id')
    user_name = session.get('user_name', 'Unknown')
    user_role = session.get('user_role', 'student')

    # ── Rate Limit Check ─────────────────────────────────────────────────
    rate_check = check_rate_limit(user_id)
    if not rate_check['allowed']:
        flash(f"⚠️ {rate_check['message']} Try again in {rate_check['reset_in']}.", 'warning')
        return redirect(request.referrer or url_for('index'))

    # ── Get form data ────────────────────────────────────────────────────
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    content_type = request.form.get('content_type', 'general')  # notes, achievements, news
    category = request.form.get('category', 'General').strip()
    subject = request.form.get('subject', '').strip()

    # ── Handle file upload ───────────────────────────────────────────────
    filename = None
    file = request.files.get('file') or request.files.get('certificate') or request.files.get('image')
    if file and file.filename != '':
        filename = file.filename

    # ── Run validation engine ────────────────────────────────────────────
    def get_target_collection():
        """Returns the collection to check duplicates against."""
        if content_type == 'notes':
            return get_col('notes')
        elif content_type == 'achievements':
            return get_col('achievements')
        elif content_type == 'news':
            return get_col('news')
        return get_col('submitted_content')

    validation = validate_submission(
        title=title,
        content=content,
        content_type=content_type,
        filename=filename,
        collection_func=get_target_collection
    )

    # ── Record submission in rate limiter ─────────────────────────────────
    record_submission(user_id)

    # ── Store submission in the submitted_content collection ─────────────
    submissions_col = get_col('submitted_content')
    submission_doc = {
        'title': title,
        'content': content,
        'content_type': content_type,
        'category': category,
        'subject': subject,
        'filename': filename,
        'submitted_by': user_name,
        'submitted_by_id': user_id,
        'submitted_by_role': user_role,
        'status': validation['status'],
        'confidence_score': validation['confidence_score'],
        'decision_reason': validation['decision_reason'],
        'validation_flags': validation['flags'],
        'ml_score': validation['breakdown']['ml_prediction']['ml_score'],
        'api_score': validation['breakdown']['api_checks']['api_score'],
        'content_score': validation['breakdown']['content_analysis']['score'],
        'created_at': datetime.utcnow().isoformat()
    }
    submissions_col.insert_one(submission_doc)

    # ── If approved, also save file and publish to target collection ──────
    if validation['status'] == 'approved':
        # Save file if uploaded
        if file and filename:
            upload_dir = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))

        # Publish to the appropriate collection
        _publish_content(title, content, content_type, category, subject,
                         filename, user_name, 'auto_validation')
        flash(f'✅ Your {content_type} submission was auto-approved! (Score: {validation["confidence_score"]})', 'success')

    elif validation['status'] == 'pending':
        # Save file for later if needed
        if file and filename:
            upload_dir = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
        flash(f'🔍 Your submission is under review by the community. (Score: {validation["confidence_score"]})', 'info')

    else:  # rejected
        reasons = ', '.join(validation['flags'][:3]) if validation['flags'] else validation['decision_reason']
        flash(f'❌ Submission rejected: {reasons}', 'danger')

    return redirect(request.referrer or url_for('index'))


def _publish_content(title, content, content_type, category, subject,
                     filename, user_name, source):
    """
    Publish approved content to the final/target collection.
    Also stores a record in the final_content collection for audit.
    """
    now = datetime.utcnow()

    if content_type == 'notes':
        get_col('notes').insert_one({
            'title': title,
            'subject': subject or 'General',
            'filename': filename,
            'uploaded_by': user_name,
            'date': now,
            'source': source
        })
    elif content_type == 'achievements':
        get_col('achievements').insert_one({
            'title': title,
            'description': content,
            'image': filename,
            'uploaded_by': user_name,
            'date': now.strftime('%Y-%m-%d'),
            'source': source
        })
    elif content_type == 'news':
        get_col('news').insert_one({
            'title': title,
            'content': content,
            'category': category or 'General',
            'image': filename,
            'date': now.strftime('%b %d, %Y'),
            'source': source
        })

    # Also store in finalized audit trail
    get_col('final_content').insert_one({
        'title': title,
        'content_type': content_type,
        'label': 'approved',
        'source': source,
        'published_by': user_name,
        'created_at': now.isoformat()
    })


# ══════════════════════════════════════════════════════════════════════════════
#  NEW MODULE: Community Voting System
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /pending-content → View content available for voting ─────────────────
@app.route('/pending-content')
@login_required
def pending_content():
    """Show all submissions with 'pending' status for community voting."""
    col = get_col('submitted_content')
    pending = list(col.find({'status': 'pending'}))

    # Attach vote tallies to each submission
    for item in pending:
        item['votes'] = get_vote_tally(str(item['_id']), get_col)

    return render_template('pending_content.html', submissions=pending)


# ── POST /vote → Cast a vote on pending content ─────────────────────────────
@app.route('/vote', methods=['POST'])
@login_required
def vote():
    """
    Cast a vote (approve/reject) on a pending submission.
    Each user can only vote once per submission.
    Votes are weighted by role (student=1, faculty=3, admin=5).
    """
    submission_id = request.form.get('submission_id')
    vote_type = request.form.get('vote_type')  # 'approve' or 'reject'

    if vote_type not in ('approve', 'reject'):
        flash('Invalid vote type.', 'danger')
        return redirect(url_for('pending_content'))

    result = cast_vote(
        submission_id=submission_id,
        user_id=session.get('user_id'),
        user_role=session.get('user_role', 'student'),
        vote_type=vote_type,
        get_col_func=get_col
    )

    if result['success']:
        flash(f'✅ {result["message"]}', 'success')

        # If community vote resulted in approval, publish the content
        decision = result.get('decision', {})
        if decision.get('decided') and decision.get('new_status') == 'approved':
            sub_col = get_col('submitted_content')
            try:
                sub = sub_col.find_one({'_id': ObjectId(submission_id)})
            except Exception:
                sub = sub_col.find_one({'_id': submission_id})

            if sub:
                _publish_content(
                    sub.get('title', ''),
                    sub.get('content', ''),
                    sub.get('content_type', 'general'),
                    sub.get('category', 'General'),
                    sub.get('subject', ''),
                    sub.get('filename'),
                    sub.get('submitted_by', 'Unknown'),
                    'community_vote'
                )
                flash('🎉 This submission has been approved by the community and published!', 'success')
    else:
        flash(f'⚠️ {result["message"]}', 'warning')

    return redirect(url_for('pending_content'))


# ══════════════════════════════════════════════════════════════════════════════
#  NEW MODULE: Admin Content Review
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/review-content')
@login_required
@role_required('admin')
def admin_review_content():
    """Admin panel to view and manage all submitted content."""
    col = get_col('submitted_content')
    all_submissions = list(col.find())

    # Sort by status: pending first, then by date descending
    status_order = {'pending': 0, 'approved': 1, 'rejected': 2}
    all_submissions.sort(key=lambda x: (
        status_order.get(x.get('status', 'pending'), 3),
        x.get('created_at', '')
    ))

    # Attach vote tallies
    for item in all_submissions:
        item['votes'] = get_vote_tally(str(item['_id']), get_col)

    return render_template('admin_review.html', submissions=all_submissions)


@app.route('/admin/approve-content/<submission_id>')
@login_required
@role_required('admin')
def admin_approve_content(submission_id):
    """Admin manually approves a pending submission."""
    col = get_col('submitted_content')

    try:
        sub = col.find_one({'_id': ObjectId(submission_id)})
        query = {'_id': ObjectId(submission_id)}
    except Exception:
        sub = col.find_one({'_id': submission_id})
        query = {'_id': submission_id}

    if not sub:
        flash('Submission not found.', 'danger')
        return redirect(url_for('admin_review_content'))

    # Update status
    col.update_one(query, {'$set': {
        'status': 'approved',
        'decided_by': 'admin',
        'decision_reason': 'Manually approved by admin'
    }})

    # Publish to target collection
    _publish_content(
        sub.get('title', ''),
        sub.get('content', ''),
        sub.get('content_type', 'general'),
        sub.get('category', 'General'),
        sub.get('subject', ''),
        sub.get('filename'),
        sub.get('submitted_by', 'Unknown'),
        'admin_approval'
    )

    flash(f'✅ Content "{sub.get("title", "")}" approved and published.', 'success')
    return redirect(url_for('admin_review_content'))


@app.route('/admin/reject-content/<submission_id>')
@login_required
@role_required('admin')
def admin_reject_content(submission_id):
    """Admin manually rejects a pending submission."""
    col = get_col('submitted_content')

    try:
        query = {'_id': ObjectId(submission_id)}
    except Exception:
        query = {'_id': submission_id}

    col.update_one(query, {'$set': {
        'status': 'rejected',
        'decided_by': 'admin',
        'decision_reason': 'Manually rejected by admin'
    }})

    flash('❌ Content rejected.', 'warning')
    return redirect(url_for('admin_review_content'))


# ══════════════════════════════════════════════════════════════════════════════
#  NEW MODULE: REST API Endpoints (JSON)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/submit-content', methods=['POST'])
def api_submit_content():
    """
    REST API: Submit content for validation.
    
    POST JSON body:
    {
        "title": "My Research Paper",
        "content": "Description of the paper...",
        "content_type": "achievements",
        "category": "Research"
    }
    
    Returns JSON with validation result, confidence score, and detailed breakdown.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    content_type = data.get('content_type', 'general')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    # Rate limit check
    rate_check = check_rate_limit(session['user_id'])
    if not rate_check['allowed']:
        return jsonify({'error': rate_check['message'], 'reset_in': rate_check['reset_in']}), 429

    # Run validation
    validation = validate_submission(title=title, content=content, content_type=content_type)
    record_submission(session['user_id'])

    return jsonify({
        'status': validation['status'],
        'confidence_score': validation['confidence_score'],
        'decision_reason': validation['decision_reason'],
        'breakdown': {
            'ml_prediction': {
                'score': validation['breakdown']['ml_prediction']['ml_score'],
                'prediction': validation['breakdown']['ml_prediction']['prediction']
            },
            'api_result': {
                'score': validation['breakdown']['api_checks']['api_score'],
                'passed': validation['breakdown']['api_checks']['passed']
            },
            'content_analysis': {
                'score': validation['breakdown']['content_analysis']['score'],
                'quality': validation['breakdown']['content_analysis']['quality_level']
            }
        },
        'flags': validation['flags']
    }), 200


@app.route('/api/pending-content', methods=['GET'])
def api_pending_content():
    """REST API: Get all pending submissions available for voting."""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    col = get_col('submitted_content')
    pending = list(col.find({'status': 'pending'}))

    results = []
    for item in pending:
        item_id = str(item.get('_id', ''))
        tally = get_vote_tally(item_id, get_col)
        results.append({
            'id': item_id,
            'title': item.get('title'),
            'content': item.get('content'),
            'content_type': item.get('content_type'),
            'submitted_by': item.get('submitted_by'),
            'confidence_score': item.get('confidence_score'),
            'created_at': item.get('created_at'),
            'votes': tally
        })

    return jsonify({'pending_count': len(results), 'submissions': results}), 200


@app.route('/api/vote', methods=['POST'])
def api_vote():
    """
    REST API: Cast a vote on pending content.
    
    POST JSON body:
    {
        "submission_id": "abc123",
        "vote_type": "approve"  // or "reject"
    }
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    submission_id = data.get('submission_id')
    vote_type = data.get('vote_type')

    if vote_type not in ('approve', 'reject'):
        return jsonify({'error': 'vote_type must be "approve" or "reject"'}), 400

    result = cast_vote(
        submission_id=submission_id,
        user_id=session['user_id'],
        user_role=session.get('user_role', 'student'),
        vote_type=vote_type,
        get_col_func=get_col
    )

    status_code = 200 if result['success'] else 409
    return jsonify(result), status_code


@app.route('/api/content-result/<submission_id>', methods=['GET'])
def api_content_result(submission_id):
    """
    REST API: Get the result of a content submission with full breakdown.
    
    Returns: status, confidence score, reason breakdown (ML, API, content analysis)
    """
    col = get_col('submitted_content')

    try:
        sub = col.find_one({'_id': ObjectId(submission_id)})
    except Exception:
        sub = col.find_one({'_id': submission_id})

    if not sub:
        return jsonify({'error': 'Submission not found'}), 404

    return jsonify({
        'id': str(sub.get('_id', '')),
        'title': sub.get('title'),
        'status': sub.get('status'),
        'confidence_score': sub.get('confidence_score'),
        'decision_reason': sub.get('decision_reason'),
        'breakdown': {
            'ml_score': sub.get('ml_score'),
            'api_score': sub.get('api_score'),
            'content_score': sub.get('content_score')
        },
        'flags': sub.get('validation_flags', []),
        'submitted_by': sub.get('submitted_by'),
        'created_at': sub.get('created_at'),
        'votes': get_vote_tally(str(sub.get('_id', '')), get_col)
    }), 200


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)
    
    # Initialize settings if missing
    with app.app_context():
        scol = get_col('settings')
        if scol is not None and scol.count_documents({"site_id": "main_config"}) == 0:
            scol.insert_one(DEFAULT_SETTINGS)
            
    app.run(debug=True, port=5000)
