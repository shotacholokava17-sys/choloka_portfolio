from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False, default='ზოგადი')
    year = db.Column(db.String(20), nullable=False, default='2025')
    short_desc = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    external_link = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    gallery_images = db.relationship('GalleryImage', backref='activity', cascade='all, delete-orphan', lazy=True)
    attachments = db.relationship('ActivityFile', backref='activity', cascade='all, delete-orphan', lazy=True)

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)

class ActivityFile(db.Model):
    __tablename__ = 'activity_files'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False, default='document')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    short_desc = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    demo_link = db.Column(db.String(255), nullable=True)
    github_link = db.Column(db.String(255), nullable=True)
    tech_stack = db.Column(db.String(255), nullable=True, default='Python, Flask')
    year = db.Column(db.String(20), default='2026')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    issuer = db.Column(db.String(255), nullable=True)
    year = db.Column(db.String(20), default='2025')
    short_desc = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='folder')

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), default='შოთა ჭოლოკავა')
    title_badge = db.Column(db.String(255), default='STEM & STEM LAB MENTOR | ROBOTICS ATHLETE')
    main_heading = db.Column(db.String(255), default='გამარჯობა, მე ვარ შოთა ჭოლოკავა')
    bio_text = db.Column(db.Text, default='ტექნოლოგიებით, რობოტექნიკითა და პროგრამირებით დაინტერესებული ახალგაზრდა ინჟინერი. საქართველოს რობოტექნიკის ეროვნული ნაკრების წევრი (FIRST Global Panama 2025, Erzurum Turkey), TBC Tech School-ის AI & Backend-ის კურსდამთავრებული, STEM Lab-ის დამფუძნებელი და მრავალი ეროვნული კონკურსისა თუ ჩემპიონატის გამარჯვებული.')
    school_info = db.Column(db.String(255), default='ქუთაისის #33 საჯარო სკოლა')
    status_badge = db.Column(db.String(255), default='აქტიური დეველოპერი & მენტორი')
    avatar_image = db.Column(db.String(255), nullable=True)
    
    # Stats
    stat_1_val = db.Column(db.String(50), default='50+')
    stat_1_lbl = db.Column(db.String(100), default='აქტივობა & პროექტი')
    stat_2_val = db.Column(db.String(50), default='1-ლი')
    stat_2_lbl = db.Column(db.String(100), default='ადგილი ეროვნულ კონფერენციაზე')
    stat_3_val = db.Column(db.String(50), default='2026')
    stat_3_lbl = db.Column(db.String(100), default='CERN Masterclass KIU')
    
    # Highlights / Roles
    role_1 = db.Column(db.String(255), default='FIRST Global 2025 Panama')
    role_2 = db.Column(db.String(255), default='Backend Python & AI (TBC Tech School)')
    role_3 = db.Column(db.String(255), default='ტოპ 3 ტექსტურ პროგრამირებაში (ROCO Academy)')
    role_4 = db.Column(db.String(255), default='ხელბურთელი (მეკარე)')

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
