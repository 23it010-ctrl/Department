from app import app, db, Setting, User, DEFAULT_SETTINGS
from werkzeug.security import generate_password_hash
import json

with app.app_context():
    # Create tables
    db.create_all()
    print("[OK] SQL Tables created.")

    # Seed initial configuration
    if Setting.query.filter_by(site_id='main_config').first() is None:
        new_setting = Setting(
            site_id='main_config',
            data_json=json.dumps(DEFAULT_SETTINGS)
        )
        db.session.add(new_setting)
        
    # Seed built-in admin if not exists
    if User.query.filter_by(email='admin@dept.com').first() is None:
        admin = User(
            name='Admin',
            email='admin@dept.com',
            password=generate_password_hash('Admin@1234'),
            role='admin',
            approved=True,
            status='approved'
        )
        db.session.add(admin)
        
    db.session.commit()
    print("[OK] Database seeded with default settings and admin user.")
