import os
import shutil
import uuid
import zipfile
import xml.etree.ElementTree as ET
from flask import Flask
from models import db, Activity, GalleryImage, ActivityFile, Category, UserProfile, AdminUser

# Setup Flask application context for DB init
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

BASE_ACTIVITIES_DIR = r'c:\Users\USER\Desktop\პორთფოლი 2020დან\აქტივობები'
UPLOADS_DIR = r'c:\Users\USER\Desktop\პორთფოლი 2020დან\static\uploads'

def extract_docx_text(filepath):
    try:
        with zipfile.ZipFile(filepath) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            texts = [node.text for node in tree.iter() if node.text]
            return ' '.join(texts).strip()
    except Exception:
        return ''

def get_category_and_year(folder_name):
    f_lower = folder_name.lower()
    
    # Year detection
    year = '2025'
    for y in ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019']:
        if y in f_lower:
            year = y
            break
            
    # Category detection
    if any(k in f_lower for k in ['რობოტ', 'stem', 'first global', 'panama', 'ერზურუმ', 'თურქეთ']):
        category = 'რობოტექნიკა & STEM'
    elif any(k in f_lower for k in ['პროგრამირებ', 'tbc', ' back end', 'კოდინგ', 'ინტელექტი', 'ai', 'ვებსაიტ']):
        category = 'პროგრამირება & AI'
    elif any(k in f_lower for k in ['ჩემპიონატ', 'ოლიმპიად', 'მაინქრაფთ', 'minecraft', 'ევერესტი', 'მოაზროვნე', 'სამშობლო']):
        category = 'ჩემპიონატები & ოლიმპიადები'
    elif any(k in f_lower for k in ['კონფერენცი', 'პიკნიკი', 'ი2q', 'i2q', 'იდეატორ', 'მილენიუმ', 'მასტერკლას', 'cern']):
        category = 'კონფერენციები'
    elif any(k in f_lower for k in ['ხელბურთ', 'სპორტ']):
        category = 'სპორტი'
    else:
        category = 'განათლება & მენტორობა'
        
    return category, year

def copy_and_sanitize_image(src_path):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        ext = '.jpg'
    new_filename = f"img_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(UPLOADS_DIR, new_filename)
    try:
        shutil.copy2(src_path, dest_path)
        return new_filename
    except Exception as e:
        print(f"Error copying {src_path}: {e}")
        return None

def copy_and_sanitize_attachment(src_path):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()
    orig_name = os.path.basename(src_path)
    new_filename = f"file_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(UPLOADS_DIR, new_filename)
    try:
        shutil.copy2(src_path, dest_path)
        f_type = 'video' if ext in ['.mp4', '.webm', '.mov', '.avi'] else 'document'
        return new_filename, orig_name, f_type
    except Exception as e:
        print(f"Error copying file {src_path}: {e}")
        return None, None, None

def seed_database():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    with app.app_context():
        db.create_all()
        
        # 1. Create Default Admin User
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser(username='admin')
            admin.set_password('shota2026')
            db.session.add(admin)
            print("Default admin created: admin / shota2026")

        # 2. Create Default UserProfile (About Me)
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile()
            db.session.add(profile)
            print("Default UserProfile created!")
            
        # 3. Categories
        categories_data = [
            ('რობოტექნიკა & STEM', 'robotics-stem', 'cpu'),
            ('პროგრამირება & AI', 'programming-ai', 'code'),
            ('ჩემპიონატები & ოლიმპიადები', 'competitions', 'trophy'),
            ('კონფერენციები', 'conferences', 'presentation'),
            ('სპორტი', 'sports', 'activity'),
            ('განათლება & მენტორობა', 'education', 'book-open'),
        ]
        
        for name, slug, icon in categories_data:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                db.session.add(Category(name=name, slug=slug, icon=icon))
        
        db.session.commit()
        
        # Clear existing activities to allow clean re-seed
        Activity.query.delete()
        GalleryImage.query.delete()
        ActivityFile.query.delete()
        db.session.commit()
        
        if not os.path.exists(BASE_ACTIVITIES_DIR):
            print(f"Directory {BASE_ACTIVITIES_DIR} does not exist.")
            return

        activity_folders = sorted(os.listdir(BASE_ACTIVITIES_DIR))
        added_count = 0
        
        for folder in activity_folders:
            folder_path = os.path.join(BASE_ACTIVITIES_DIR, folder)
            if not os.path.isdir(folder_path) or folder in ['.idea', '!დიპლომები სა სიგელები']:
                continue

            category, year = get_category_and_year(folder)
            
            images = []
            attachments = []
            docx_texts = []
            external_links = []
            
            for root, dirs, files in os.walk(folder_path):
                for file in sorted(files):
                    f_path = os.path.join(root, file)
                    f_ext = os.path.splitext(file)[1].lower()
                    
                    if f_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                        images.append(f_path)
                    elif f_ext in ['.pdf', '.docx', '.pptx', '.mp4', '.txt']:
                        attachments.append(f_path)
                        if f_ext == '.docx':
                            t = extract_docx_text(f_path)
                            if t:
                                docx_texts.append(t)
                                for word in t.split():
                                    if word.startswith('http://') or word.startswith('https://'):
                                        external_links.append(word)

            title = folder.strip()
            
            short_desc = f"{title} - შოთა ჭოლოკავას აქტივობა ({year} წელი)."
            if docx_texts:
                content = "\n\n".join(docx_texts)
                short_desc = docx_texts[0][:180] + "..." if len(docx_texts[0]) > 180 else docx_texts[0]
            else:
                content = f"შოთა ჭოლოკავას მონაწილეობა და მიღწევა: '{title}'. პროექტი/აქტივობა განხორციელდა {year} წელს."

            ext_link = external_links[0] if external_links else None

            # Copy Cover Image
            cover_filename = None
            uploaded_gallery_filenames = []
            
            for img_path in images:
                copied = copy_and_sanitize_image(img_path)
                if copied:
                    if not cover_filename:
                        cover_filename = copied
                    else:
                        uploaded_gallery_filenames.append(copied)

            act = Activity(
                title=title,
                category=category,
                year=year,
                short_desc=short_desc,
                content=content,
                cover_image=cover_filename,
                external_link=ext_link,
                is_featured=True
            )
            
            db.session.add(act)
            db.session.flush()

            # Add Gallery Images
            for g_img in uploaded_gallery_filenames:
                db.session.add(GalleryImage(
                    activity_id=act.id,
                    image_path=g_img,
                    caption=title
                ))

            # Add Document & Video Attachments
            for att_path in attachments:
                att_fn, orig_name, f_type = copy_and_sanitize_attachment(att_path)
                if att_fn:
                    db.session.add(ActivityFile(
                        activity_id=act.id,
                        file_path=att_fn,
                        original_name=orig_name,
                        file_type=f_type
                    ))

            added_count += 1

        db.session.commit()
        print(f"Successfully seeded database with {added_count} activities, galleries & attachments!")

if __name__ == '__main__':
    seed_database()
