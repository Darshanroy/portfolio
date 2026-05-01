import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")

# ---------------------------------------------------------------------------
# Supabase Lazy Loader
# ---------------------------------------------------------------------------
_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY environment variables in Vercel Dashboard.")
        _supabase_client = create_client(url, key)
    return _supabase_client

# ---------------------------------------------------------------------------
# Helper: lets Jinja templates use dot-notation (project.name, project.id, etc.)
# ---------------------------------------------------------------------------
class Row:
    """Wraps a Supabase dict so templates can use {{ row.field }} syntax."""
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def get_images(self):
        raw = getattr(self, "images", None)
        if raw is None:
            return []
        if isinstance(raw, list):
            return raw
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

def _rows(table, query_fn=None):
    supabase = get_supabase()
    q = supabase.table(table).select("*")
    if query_fn:
        q = query_fn(q)
    return [Row(r) for r in q.execute().data]

def _single(table, column, value):
    supabase = get_supabase()
    res = supabase.table(table).select("*").eq(column, value).execute()
    if not res.data:
        return None
    return Row(res.data[0])

# ---------------------------------------------------------------------------
# Production guard – block /admin on Vercel
# ---------------------------------------------------------------------------
@app.before_request
def disable_admin_in_prod():
    if os.environ.get("VERCEL") and request.path.startswith("/admin"):
        abort(404)

# ═══════════════════════════════════════════════════════════════════════════
#  DIAGNOSTICS & PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/test-db')
def test_db():
    output = []
    # 1. Check Supabase
    try:
        supabase = get_supabase()
        res = supabase.table('projects').select('count', count='exact').execute()
        output.append(f"SUCCESS: Supabase Connected. Found {res.count} projects.")
    except Exception as e:
        output.append(f"ERROR: Supabase: {str(e)}")
    
    # 2. Check Templates
    template_path = os.path.join(app.root_path, 'templates', 'public', 'index.html')
    exists = os.path.exists(template_path)
    output.append(f"TEMPLATE CHECK: {template_path} exists? {exists}")
    
    # 3. List templates dir
    try:
        t_dir = os.path.join(app.root_path, 'templates')
        files = os.listdir(t_dir) if os.path.exists(t_dir) else "DIR NOT FOUND"
        output.append(f"TEMPLATES DIR CONTENTS: {files}")
    except Exception as e:
        output.append(f"TEMPLATES DIR ERROR: {str(e)}")

    return "<br>".join(output)

@app.route("/")
def public_index():
    try:
        projects = _rows("projects")
        skills = _rows("skills", lambda q: q.eq("type", "skill"))
        blogs = _rows("skills", lambda q: q.in_("type", ["blog", "learning"]))
        achievements = _rows("achievements")
        return render_template(
            "public/index.html",
            projects=projects,
            skills=skills,
            blogs=blogs,
            achievements=achievements,
        )
    except Exception as e:
        if os.environ.get("VERCEL"):
            return f"<h1>Deployment Error</h1><p>{str(e)}</p><p>Please ensure you have added <b>SUPABASE_URL</b> and <b>SUPABASE_KEY</b> to your Vercel Project Settings.</p>", 500
        raise e

@app.route("/project/<project_id>")
def public_project_detail(project_id):
    project = _single("projects", "id", project_id)
    if not project:
        abort(404)
    return render_template("public/project_detail.html", project=project)

@app.route("/blog")
def public_blog_list():
    blogs = _rows("skills", lambda q: q.in_("type", ["blog", "learning"]))
    return render_template("public/blog_list.html", blogs=blogs)

@app.route("/learning/<learning_id>")
def public_learning_detail(learning_id):
    item = _single("skills", "id", learning_id)
    if not item:
        abort(404)
    supabase = get_supabase()
    sections_res = supabase.table("skill_sections").select("*").eq("skill_id", learning_id).execute()
    item.sections = [Row(s) for s in sections_res.data]
    return render_template("public/learning_detail.html", item=item)

@app.route("/achievements")
def public_achievement_list():
    achievements = _rows("achievements")
    return render_template("public/achievement_list.html", achievements=achievements)

@app.route("/contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if name and email and message:
        supabase = get_supabase()
        supabase.table("contact_messages").insert({"name": name, "email": email, "message": message}).execute()
        flash("Thank you!", "success")
    return redirect(url_for("public_index") + "#contact")

@app.route("/send_resume", methods=["POST"])
def send_resume():
    user_email = request.form.get("email")
    if user_email:
        flash(f"Resume requested for {user_email}", "success")
    return redirect(url_for("public_index") + "#contact")

# ═══════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/admin")
def admin_index():
    projects = _rows("projects")
    return render_template("dashboard.html", projects=projects, skills=[], blogs=[], achievements=[])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
