import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key'

# Supabase Initialization
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Helper class to allow templates to use dot notation (e.g., project.name)
class DataWrapper:
    def __init__(self, data):
        self.__dict__.update(data)
    
    def get_images(self):
        images = getattr(self, 'images', '[]')
        import json
        if isinstance(images, list):
            return images
        try:
            return json.loads(images) if images else []
        except:
            return []

# --- PUBLIC ROUTES ---

@app.route('/')
def public_index():
    projects_data = supabase.table('projects').select('*').execute()
    skills_data = supabase.table('skills').select('*').eq('type', 'skill').execute()
    blogs_data = supabase.table('skills').select('*').in_('type', ['blog', 'learning']).execute()
    achievements_data = supabase.table('achievements').select('*').execute()
    
    projects = [DataWrapper(p) for p in projects_data.data]
    skills = [DataWrapper(s) for s in skills_data.data]
    blogs = [DataWrapper(b) for b in blogs_data.data]
    achievements = [DataWrapper(a) for a in achievements_data.data]
    
    return render_template('public/index.html', projects=projects, skills=skills, blogs=blogs, achievements=achievements)

@app.route('/project/<project_id>')
def public_project_detail(project_id):
    res = supabase.table('projects').select('*').eq('id', project_id).single().execute()
    if not res.data:
        abort(404)
    project = DataWrapper(res.data)
    return render_template('public/project_detail.html', project=project)

@app.route('/blog')
def public_blog_list():
    res = supabase.table('skills').select('*').in_('type', ['blog', 'learning']).execute()
    blogs = [DataWrapper(b) for b in res.data]
    return render_template('public/blog_list.html', blogs=blogs)

@app.route('/learning/<learning_id>')
def public_learning_detail(learning_id):
    # Fetch skill and its sections
    res = supabase.table('skills').select('*, skill_sections(*)').eq('id', learning_id).single().execute()
    if not res.data:
        abort(404)
    
    item_data = res.data
    # Convert sections to objects as well
    item_data['sections'] = [DataWrapper(s) for s in item_data.get('skill_sections', [])]
    item = DataWrapper(item_data)
    
    return render_template('public/learning_detail.html', item=item)

@app.route('/achievements')
def public_achievement_list():
    res = supabase.table('achievements').select('*').execute()
    achievements = [DataWrapper(a) for a in res.data]
    return render_template('public/achievement_list.html', achievements=achievements)

@app.route('/contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if name and email and message:
        supabase.table('contact_messages').insert({
            'name': name,
            'email': email,
            'message': message
        }).execute()
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
        
    SENDER_EMAIL = os.environ.get('MAIL_USERNAME')
    SENDER_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = 'Darshankumarr03@gmail.com'
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        msg['Bcc'] = ADMIN_EMAIL
        msg['Subject'] = "Darshan kumar - Resume"
        body = f"Hello,\n\nThank you for your interest! Please find my resume online at: {request.host_url}static/Darshan_kumar_r_resume.pdf\n\nBest,\nDarshan Kumar"
        msg.attach(MIMEText(body, 'plain'))
        
        if SENDER_EMAIL and SENDER_PASSWORD:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            flash(f'Resume sent to {user_email}!', 'success')
        else:
            flash(f'Resume sent to {user_email}! (SMTP not configured)', 'success')
            
    except Exception as e:
        print(f"Email Error: {e}")
        flash('Failed to send resume.', 'error')

    return redirect(url_for('public_index') + '#contact')

@app.before_request
def disable_admin_in_prod():
    if os.environ.get('VERCEL') and request.path.startswith('/admin'):
        abort(404)

# --- ADMIN ROUTES ---

@app.route('/admin')
def admin_index():
    projects = [DataWrapper(p) for p in supabase.table('projects').select('*').execute().data]
    skills = [DataWrapper(s) for s in supabase.table('skills').select('*').eq('type', 'skill').execute().data]
    blogs = [DataWrapper(b) for b in supabase.table('skills').select('*').in_('type', ['blog', 'learning']).execute().data]
    achievements = [DataWrapper(a) for a in supabase.table('achievements').select('*').execute().data]
    return render_template('dashboard.html', projects=projects, skills=skills, blogs=blogs, achievements=achievements)

@app.route('/admin/project/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        project_data = {
            'id': request.form['id'],
            'name': request.form['name'],
            'summary': request.form['summary'],
            'metrics': request.form.get('metrics', ''),
            'architecture': request.form.get('architecture', ''),
            'failure_handling': request.form.get('failure_handling', ''),
            'tradeoffs': request.form.get('tradeoffs', ''),
            'impact': request.form.get('impact', ''),
            'tech_stack': request.form.get('tech_stack', ''),
            'github_url': request.form.get('github_url', ''),
            'live_url': request.form.get('live_url', ''),
            'chat_url': request.form.get('chat_url', '')
        }
        images = request.form.get('images', '')
        if images:
            import json
            project_data['images'] = json.dumps([i.strip() for i in images.split(',')])
            
        supabase.table('projects').insert(project_data).execute()
        return redirect(url_for('admin_index'))
    return render_template('project_form.html', project=None)

@app.route('/admin/project/edit/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    res = supabase.table('projects').select('*').eq('id', project_id).single().execute()
    project = DataWrapper(res.data)
    if request.method == 'POST':
        update_data = {
            'name': request.form['name'],
            'summary': request.form['summary'],
            'metrics': request.form.get('metrics', ''),
            'architecture': request.form.get('architecture', ''),
            'failure_handling': request.form.get('failure_handling', ''),
            'tradeoffs': request.form.get('tradeoffs', ''),
            'impact': request.form.get('impact', ''),
            'tech_stack': request.form.get('tech_stack', ''),
            'github_url': request.form.get('github_url', ''),
            'live_url': request.form.get('live_url', ''),
            'chat_url': request.form.get('chat_url', '')
        }
        images = request.form.get('images', '')
        if images:
            import json
            update_data['images'] = json.dumps([i.strip() for i in images.split(',')])
            
        supabase.table('projects').update(update_data).eq('id', project_id).execute()
        return redirect(url_for('admin_index'))
    return render_template('project_form.html', project=project)

@app.route('/admin/project/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    supabase.table('projects').delete().eq('id', project_id).execute()
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
