import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models import db, Activity, GalleryImage, ActivityFile, Project, Certificate, Category, UserProfile, AdminUser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shota_cholokava_secret_key_2026_portfolio'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB Max Upload Limit

db.init_app(app)

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'mp4', 'webm', 'mov', 'avi', 'zip', 'rar'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

def allowed_attachment(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ATTACHMENT_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_image(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"upload_{uuid.uuid4().hex[:12]}.{ext}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

def save_uploaded_attachment(file):
    if file and (allowed_attachment(file.filename) or allowed_image(file.filename)):
        orig_name = file.filename
        ext = orig_name.rsplit('.', 1)[1].lower()
        filename = f"file_{uuid.uuid4().hex[:12]}.{ext}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        file_type = 'video' if ext in ['mp4', 'webm', 'mov', 'avi'] else 'document'
        return filename, orig_name, file_type
    return None, None, None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('გთხოვთ გაიაროთ ავტორიზაცია.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    categories = Category.query.all()
    activities = Activity.query.order_by(Activity.year.desc(), Activity.id.desc()).all()
    profile = UserProfile.query.first()
    if not profile:
        profile = UserProfile()
        db.session.add(profile)
        db.session.commit()
    return render_template('index.html', categories=categories, activities=activities, profile=profile)

@app.route('/projects')
def projects():
    projects_list = Project.query.order_by(Project.year.desc(), Project.id.desc()).all()
    return render_template('projects.html', projects=projects_list)

@app.route('/certificates')
def certificates():
    certs = Certificate.query.order_by(Certificate.year.desc(), Certificate.id.desc()).all()
    return render_template('certificates.html', certificates=certs)

@app.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    related_activities = Activity.query.filter(
        Activity.id != activity.id,
        Activity.category == activity.category
    ).limit(4).all()
    
    if len(related_activities) < 4:
        extra = Activity.query.filter(
            Activity.id != activity.id,
            ~Activity.id.in_([r.id for r in related_activities])
        ).limit(4 - len(related_activities)).all()
        related_activities.extend(extra)
        
    return render_template('detail.html', activity=activity, related_activities=related_activities)

# --- ADMIN ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_user'] = user.username
            flash('წარმატებით გაიარეთ ავტორიზაცია!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('არასწორი მომხმარებლის სახელი ან პაროლი.', 'error')

    return render_template('admin/login.html')

@app.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('გამოხვედით სისტემიდან.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    activities = Activity.query.order_by(Activity.id.desc()).all()
    projects_list = Project.query.order_by(Project.id.desc()).all()
    certs = Certificate.query.order_by(Certificate.id.desc()).all()
    categories = Category.query.all()
    total_gallery_count = GalleryImage.query.count()
    total_attachments_count = ActivityFile.query.count()
    profile = UserProfile.query.first()
    return render_template('admin/dashboard.html', 
                           activities=activities, 
                           projects=projects_list,
                           certificates=certs,
                           categories=categories, 
                           total_gallery_count=total_gallery_count,
                           total_attachments_count=total_attachments_count,
                           profile=profile)

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    profile = UserProfile.query.first()
    if not profile:
        profile = UserProfile()
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.title_badge = request.form.get('title_badge')
        profile.main_heading = request.form.get('main_heading')
        profile.bio_text = request.form.get('bio_text')
        profile.school_info = request.form.get('school_info')
        profile.status_badge = request.form.get('status_badge')
        
        profile.stat_1_val = request.form.get('stat_1_val')
        profile.stat_1_lbl = request.form.get('stat_1_lbl')
        profile.stat_2_val = request.form.get('stat_2_val')
        profile.stat_2_lbl = request.form.get('stat_2_lbl')
        profile.stat_3_val = request.form.get('stat_3_val')
        profile.stat_3_lbl = request.form.get('stat_3_lbl')
        
        profile.role_1 = request.form.get('role_1')
        profile.role_2 = request.form.get('role_2')
        profile.role_3 = request.form.get('role_3')
        profile.role_4 = request.form.get('role_4')

        avatar = save_uploaded_file(request.files.get('avatar_image'))
        if avatar:
            profile.avatar_image = avatar

        db.session.commit()
        flash('"ჩემ შესახებ" პროფილის მონაცემები წარმატებით განახლდა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/profile_form.html', profile=profile)

# --- ADMIN PROJECT ROUTES ---

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def admin_new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        short_desc = request.form.get('short_desc')
        content = request.form.get('content')
        demo_link = request.form.get('demo_link')
        github_link = request.form.get('github_link')
        tech_stack = request.form.get('tech_stack', 'Python, Flask')
        year = request.form.get('year', '2026')
        
        cover_image = save_uploaded_file(request.files.get('cover_image'))

        proj = Project(
            title=title,
            short_desc=short_desc,
            content=content,
            cover_image=cover_image,
            demo_link=demo_link,
            github_link=github_link,
            tech_stack=tech_stack,
            year=year
        )
        db.session.add(proj)
        db.session.commit()
        flash('ახალი პროექტი წარმატებით დაემატა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/project_form.html', project=None)

@app.route('/admin/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_project(project_id):
    proj = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        proj.title = request.form.get('title')
        proj.short_desc = request.form.get('short_desc')
        proj.content = request.form.get('content')
        proj.demo_link = request.form.get('demo_link')
        proj.github_link = request.form.get('github_link')
        proj.tech_stack = request.form.get('tech_stack')
        proj.year = request.form.get('year')

        new_cover = save_uploaded_file(request.files.get('cover_image'))
        if new_cover:
            proj.cover_image = new_cover

        db.session.commit()
        flash('პროექტი წარმატებით განახლდა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/project_form.html', project=proj)

@app.route('/admin/project/delete/<int:project_id>', methods=['POST'])
@login_required
def admin_delete_project(project_id):
    proj = Project.query.get_or_404(project_id)
    db.session.delete(proj)
    db.session.commit()
    flash('პროექტი წარმატებით წაიშალა!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- ADMIN CERTIFICATE ROUTES ---

@app.route('/admin/certificate/new', methods=['GET', 'POST'])
@login_required
def admin_new_certificate():
    if request.method == 'POST':
        title = request.form.get('title')
        issuer = request.form.get('issuer')
        year = request.form.get('year', '2025')
        short_desc = request.form.get('short_desc')
        
        image_path = save_uploaded_file(request.files.get('image_path'))

        cert = Certificate(
            title=title,
            issuer=issuer,
            year=year,
            short_desc=short_desc,
            image_path=image_path
        )
        db.session.add(cert)
        db.session.commit()
        flash('სერტიფიკატი / დიპლომი წარმატებით დაემატა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/certificate_form.html', certificate=None)

@app.route('/admin/certificate/edit/<int:cert_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    
    if request.method == 'POST':
        cert.title = request.form.get('title')
        cert.issuer = request.form.get('issuer')
        cert.year = request.form.get('year')
        cert.short_desc = request.form.get('short_desc')

        new_img = save_uploaded_file(request.files.get('image_path'))
        if new_img:
            cert.image_path = new_img

        db.session.commit()
        flash('სერტიფიკატი წარმატებით განახლდა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/certificate_form.html', certificate=cert)

@app.route('/admin/certificate/delete/<int:cert_id>', methods=['POST'])
@login_required
def admin_delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    db.session.delete(cert)
    db.session.commit()
    flash('სერტიფიკატი წაიშალა!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- ADMIN ACTIVITY ROUTES ---

@app.route('/admin/activity/new', methods=['GET', 'POST'])
@login_required
def admin_new_activity():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        year = request.form.get('year', '2025')
        short_desc = request.form.get('short_desc')
        content = request.form.get('content')
        external_link = request.form.get('external_link')

        cover_image = save_uploaded_file(request.files.get('cover_image'))

        act = Activity(
            title=title,
            category=category,
            year=year,
            short_desc=short_desc,
            content=content,
            cover_image=cover_image,
            external_link=external_link
        )
        db.session.add(act)
        db.session.flush()

        # Handle Multiple Gallery Uploads
        gallery_files = request.files.getlist('gallery_images')
        for g_file in gallery_files:
            g_filename = save_uploaded_file(g_file)
            if g_filename:
                db.session.add(GalleryImage(activity_id=act.id, image_path=g_filename))

        # Handle Document & Video Attachments Upload
        attachment_files = request.files.getlist('attachment_files')
        for att_file in attachment_files:
            att_fn, orig_name, f_type = save_uploaded_attachment(att_file)
            if att_fn:
                db.session.add(ActivityFile(
                    activity_id=act.id, 
                    file_path=att_fn, 
                    original_name=orig_name, 
                    file_type=f_type
                ))

        db.session.commit()
        flash('ახალი აქტივობა წარმატებით დაემატა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/activity_form.html', categories=categories, activity=None)

@app.route('/admin/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    categories = Category.query.all()

    if request.method == 'POST':
        activity.title = request.form.get('title')
        activity.category = request.form.get('category')
        activity.year = request.form.get('year')
        activity.short_desc = request.form.get('short_desc')
        activity.content = request.form.get('content')
        activity.external_link = request.form.get('external_link')

        # Optional Cover Image update
        new_cover = save_uploaded_file(request.files.get('cover_image'))
        if new_cover:
            activity.cover_image = new_cover

        # Append Gallery Uploads
        gallery_files = request.files.getlist('gallery_images')
        for g_file in gallery_files:
            g_filename = save_uploaded_file(g_file)
            if g_filename:
                db.session.add(GalleryImage(activity_id=activity.id, image_path=g_filename))

        # Append Document & Video Attachments
        attachment_files = request.files.getlist('attachment_files')
        for att_file in attachment_files:
            att_fn, orig_name, f_type = save_uploaded_attachment(att_file)
            if att_fn:
                db.session.add(ActivityFile(
                    activity_id=activity.id, 
                    file_path=att_fn, 
                    original_name=orig_name, 
                    file_type=f_type
                ))

        db.session.commit()
        flash('აქტივობა წარმატებით განახლდა!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/activity_form.html', categories=categories, activity=activity)

@app.route('/admin/activity/delete/<int:activity_id>', methods=['POST'])
@login_required
def admin_delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    flash('აქტივობა წარმატებით წაიშალა!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/gallery/delete/<int:image_id>')
@login_required
def admin_delete_gallery_image(image_id):
    img = GalleryImage.query.get_or_404(image_id)
    act_id = img.activity_id
    db.session.delete(img)
    db.session.commit()
    flash('ფოტო წაიშალა გალერეიდან.', 'success')
    return redirect(url_for('admin_edit_activity', activity_id=act_id))

@app.route('/admin/attachment/delete/<int:file_id>')
@login_required
def admin_delete_attachment(file_id):
    att = ActivityFile.query.get_or_404(file_id)
    act_id = att.activity_id
    db.session.delete(att)
    db.session.commit()
    flash('ფაილი წაიშალა.', 'success')
    return redirect(url_for('admin_edit_activity', activity_id=act_id))

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            slug = name.lower().replace(' ', '-').replace('&', 'and')
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, slug=slug))
                db.session.commit()
                flash('კატეგორია დაემატა!', 'success')
            else:
                flash('ასეთი კატეგორია უკვე არსებობს.', 'error')

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting Shota Cholokava Portfolio Web Server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
