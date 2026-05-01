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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in .env or environment variables.\n"
        "Example .env:\n"
        "  SUPABASE_URL=https://xxxxx.supabase.co\n"
        "  SUPABASE_KEY=eyJhbGci..."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        except (json.JSONDecodeError, TypeError):
            return []


def _rows(table, query_fn=None):
    """Fetch rows from a Supabase table and return a list of Row objects.
    
    query_fn takes a SelectRequestBuilder and returns it after applying filters.
    Example: _rows('projects')
             _rows('skills', lambda q: q.eq('type', 'skill'))
    """
    q = supabase.table(table).select("*")
    if query_fn:
        q = query_fn(q)
    return [Row(r) for r in q.execute().data]


def _single(table, column, value):
    """Fetch a single row or return None."""
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
    try:
        if not SUPABASE_URL:
            return "ERROR: SUPABASE_URL is missing from environment variables.", 500
        if not SUPABASE_KEY:
            return "ERROR: SUPABASE_KEY is missing from environment variables.", 500
        
        # Test query
        res = supabase.table('projects').select('count', count='exact').execute()
        return f"SUCCESS: Connected to Supabase. Found {res.count} projects."
    except Exception as e:
        return f"ERROR: Could not connect to Supabase: {str(e)}", 500

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
        # In production, show a slightly better error or at least the message for debugging
        if os.environ.get("VERCEL"):
            return f"<h1>Database Connection Error</h1><p>The application could not reach Supabase. Please ensure your <b>SUPABASE_URL</b> and <b>SUPABASE_KEY</b> are correctly set in the Vercel Dashboard.</p><p>Technical details: {str(e)}</p>", 500
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
    # Fetch the skill
    item = _single("skills", "id", learning_id)
    if not item:
        abort(404)
    # Fetch its sections
    sections_res = (
        supabase.table("skill_sections")
        .select("*")
        .eq("skill_id", learning_id)
        .execute()
    )
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
        supabase.table("contact_messages").insert(
            {"name": name, "email": email, "message": message}
        ).execute()
        flash("Thank you for reaching out. I will get back to you soon!", "success")
    else:
        flash("Please fill out all required fields.", "error")

    return redirect(url_for("public_index") + "#contact")


@app.route("/send_resume", methods=["POST"])
def send_resume():
    user_email = request.form.get("email")
    if not user_email:
        flash("Please enter your email.", "error")
        return redirect(url_for("public_index") + "#contact")

    sender = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_PASSWORD")
    admin = "Darshankumarr03@gmail.com"

    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = user_email
        msg["Bcc"] = admin
        msg["Subject"] = "Darshan Kumar – Resume"
        body = (
            f"Hello,\n\n"
            f"Thank you for your interest! You can view my resume at:\n"
            f"{request.host_url}static/Darshan_kumar_r_resume.pdf\n\n"
            f"Best,\nDarshan Kumar"
        )
        msg.attach(MIMEText(body, "plain"))

        if sender and password:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            flash(f"Resume sent to {user_email}!", "success")
        else:
            flash(f"Resume sent to {user_email}! (SMTP not configured)", "success")

    except Exception as e:
        print(f"Email Error: {e}")
        flash("Failed to send resume.", "error")

    return redirect(url_for("public_index") + "#contact")


# ═══════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES  (blocked in production by before_request hook above)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/admin")
def admin_index():
    projects = _rows("projects")
    skills = _rows("skills", lambda q: q.eq("type", "skill"))
    blogs = _rows("skills", lambda q: q.in_("type", ["blog", "learning"]))
    achievements = _rows("achievements")
    return render_template(
        "dashboard.html",
        projects=projects,
        skills=skills,
        blogs=blogs,
        achievements=achievements,
    )


@app.route("/admin/project/new", methods=["GET", "POST"])
def new_project():
    if request.method == "POST":
        data = {
            "id": request.form["id"],
            "name": request.form["name"],
            "summary": request.form["summary"],
            "metrics": request.form.get("metrics", ""),
            "architecture": request.form.get("architecture", ""),
            "failure_handling": request.form.get("failure_handling", ""),
            "tradeoffs": request.form.get("tradeoffs", ""),
            "impact": request.form.get("impact", ""),
            "tech_stack": request.form.get("tech_stack", ""),
            "github_url": request.form.get("github_url", ""),
            "live_url": request.form.get("live_url", ""),
            "chat_url": request.form.get("chat_url", ""),
        }
        images_raw = request.form.get("images", "")
        if images_raw:
            data["images"] = json.dumps([i.strip() for i in images_raw.split(",")])
        supabase.table("projects").insert(data).execute()
        return redirect(url_for("admin_index"))
    return render_template("project_form.html", project=None)


@app.route("/admin/project/edit/<project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    project = _single("projects", "id", project_id)
    if not project:
        abort(404)
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "summary": request.form["summary"],
            "metrics": request.form.get("metrics", ""),
            "architecture": request.form.get("architecture", ""),
            "failure_handling": request.form.get("failure_handling", ""),
            "tradeoffs": request.form.get("tradeoffs", ""),
            "impact": request.form.get("impact", ""),
            "tech_stack": request.form.get("tech_stack", ""),
            "github_url": request.form.get("github_url", ""),
            "live_url": request.form.get("live_url", ""),
            "chat_url": request.form.get("chat_url", ""),
        }
        images_raw = request.form.get("images", "")
        if images_raw:
            data["images"] = json.dumps([i.strip() for i in images_raw.split(",")])
        supabase.table("projects").update(data).eq("id", project_id).execute()
        return redirect(url_for("admin_index"))
    return render_template("project_form.html", project=project)


@app.route("/admin/project/delete/<project_id>", methods=["POST"])
def delete_project(project_id):
    supabase.table("projects").delete().eq("id", project_id).execute()
    return redirect(url_for("admin_index"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
