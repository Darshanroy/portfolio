import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from models import db, Project, Skill, SkillSection, Achievement, ContactMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Use DATABASE_URL if available, else fallback to SQLite
db_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'admin.db'))
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

# --- PUBLIC ROUTES ---

@app.route('/')
def public_index():
    projects = Project.query.all()
    skills = Skill.query.filter_by(type='skill').all()
    blogs = Skill.query.filter(Skill.type.in_(['blog', 'learning'])).all()
    achievements = Achievement.query.all()
    return render_template('public/index.html', projects=projects, skills=skills, blogs=blogs, achievements=achievements)

@app.route('/project/<project_id>')
def public_project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('public/project_detail.html', project=project)

@app.route('/blog')
def public_blog_list():
    blogs = Skill.query.filter(Skill.type.in_(['blog', 'learning'])).all()
    return render_template('public/blog_list.html', blogs=blogs)

@app.route('/learning/<learning_id>')
def public_learning_detail(learning_id):
    item = Skill.query.get_or_404(learning_id)
    return render_template('public/learning_detail.html', item=item)

@app.route('/achievements')
def public_achievement_list():
    achievements = Achievement.query.all()
    return render_template('public/achievement_list.html', achievements=achievements)

@app.route('/contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if name and email and message:
        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash('Thank you for reaching out. I will get back to you soon!', 'success')
    else:
        flash('Please fill out all required fields.', 'error')
        
    return redirect(url_for('public_index') + '#contact')

@app.route('/send_resume', methods=['POST'])
def send_resume():
    user_email = request.form.get('email')
    
    if not user_email:
        flash('Please enter your email.', 'error')
        return redirect(url_for('public_index') + '#contact')
        
    # Email configuration - User needs to set these in their environment or .env
    SENDER_EMAIL = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
    SENDER_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your_app_password')
    ADMIN_EMAIL = 'Darshankumarr03@gmail.com'
    
    try:
        # Create the message for the user
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        msg['Bcc'] = ADMIN_EMAIL
        msg['Subject'] = "Darshan kumar - Resume"
        body = f"Hello,\n\nThank you for your interest! Please find my resume online at: {request.host_url}static/Darshan_kumar_r_resume.pdf\n\nBest,\nDarshan Kumar"
        msg.attach(MIMEText(body, 'plain'))
        
        # Only attempt to send if credentials are changed from defaults
        if SENDER_EMAIL != 'your_email@gmail.com' and SENDER_PASSWORD != 'your_app_password':
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            flash(f'Resume sent to {user_email}!', 'success')
        else:
            # Mock success if no credentials provided so UI still works
            print(f"[MOCK EMAIL] Sent resume to {user_email}")
            print(f"[MOCK EMAIL] Notified {ADMIN_EMAIL}")
            flash(f'Resume sent to {user_email}! (Mocked - configure SMTP in app.py)', 'success')
            
    except Exception as e:
        print(f"Email Error: {e}")
        flash('Failed to send resume. Please check server configuration.', 'error')

    return redirect(url_for('public_index') + '#contact')


from flask import abort

@app.before_request
def disable_admin_in_prod():
    # Disable all admin endpoints in production (Vercel)
    if os.environ.get('VERCEL') and request.path.startswith('/admin'):
        abort(404)

# --- ADMIN ROUTES ---

@app.route('/admin')
def admin_index():
    projects = Project.query.all()
    skills = Skill.query.filter_by(type='skill').all()
    blogs = Skill.query.filter(Skill.type.in_(['blog', 'learning'])).all()
    achievements = Achievement.query.all()
    return render_template('dashboard.html', projects=projects, skills=skills, blogs=blogs, achievements=achievements)

@app.route('/admin/project/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        project = Project(
            id=request.form['id'],
            name=request.form['name'],
            summary=request.form['summary'],
            metrics=request.form.get('metrics', ''),
            architecture=request.form.get('architecture', ''),
            failure_handling=request.form.get('failure_handling', ''),
            tradeoffs=request.form.get('tradeoffs', ''),
            impact=request.form.get('impact', ''),
            tech_stack=request.form.get('tech_stack', ''),
            github_url=request.form.get('github_url', ''),
            live_url=request.form.get('live_url', ''),
            chat_url=request.form.get('chat_url', '')
        )
        images = request.form.get('images', '')
        if images:
            project.set_images([i.strip() for i in images.split(',')])
            
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('admin_index'))
    return render_template('project_form.html', project=None)

@app.route('/admin/project/edit/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.summary = request.form['summary']
        project.metrics = request.form.get('metrics', '')
        project.architecture = request.form.get('architecture', '')
        project.failure_handling = request.form.get('failure_handling', '')
        project.tradeoffs = request.form.get('tradeoffs', '')
        project.impact = request.form.get('impact', '')
        project.tech_stack = request.form.get('tech_stack', '')
        project.github_url = request.form.get('github_url', '')
        project.live_url = request.form.get('live_url', '')
        project.chat_url = request.form.get('chat_url', '')
        
        images = request.form.get('images', '')
        if images:
            project.set_images([i.strip() for i in images.split(',')])
            
        db.session.commit()
        return redirect(url_for('admin_index'))
    return render_template('project_form.html', project=project)

@app.route('/admin/project/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
