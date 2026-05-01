import os
import asyncio
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from dotenv import load_dotenv
from database import SupabaseService

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

# Resolve paths relative to THIS file — critical for Vercel (/var/task/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")

# ---------------------------------------------------------------------------
# Global Error Handler (shows full traceback on Vercel)
# ---------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    print(f"ERROR: {e}\n{tb}")
    return f"<h1>Error</h1><pre>{tb}</pre>", 500

# ---------------------------------------------------------------------------
# Production guard – block /admin on Vercel
# ---------------------------------------------------------------------------
@app.before_request
def disable_admin_in_prod():
    if os.environ.get("VERCEL") and request.path.startswith("/admin"):
        abort(404)

# ═══════════════════════════════════════════════════════════════════════════
#  PUBLIC ROUTES (FAST INFERENCE / LOCAL-FIRST)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/debug-files")
def debug_files():
    """Temporary route to verify Vercel has all files. DELETE after confirming."""
    import json
    result = {"BASE_DIR": BASE_DIR, "files": {}}
    for folder in ["templates", "static"]:
        full = os.path.join(BASE_DIR, folder)
        try:
            result["files"][folder] = os.listdir(full)
        except FileNotFoundError:
            result["files"][folder] = "NOT FOUND"
    return f"<pre>{json.dumps(result, indent=2)}</pre>"

@app.route("/")
async def public_index():
    projects, skills, blogs, achievements = await asyncio.gather(
        SupabaseService.get_projects(),
        SupabaseService.get_skills(skill_type="skill"),
        SupabaseService.get_skills_by_types(["blog", "learning"]),
        SupabaseService.get_achievements(),
    )
    return render_template(
        "index.html",
        projects=projects,
        skills=skills,
        blogs=blogs,
        achievements=achievements,
    )

@app.route("/project/<project_id>")
async def public_project_detail(project_id):
    project = await SupabaseService.get_project(project_id)
    if not project:
        abort(404)
    return render_template("project_detail.html", project=project)

@app.route("/learning/<learning_id>")
async def public_learning_detail(learning_id):
    learning = await SupabaseService.get_skill_with_sections(learning_id)
    if not learning:
        abort(404)
    return render_template("learning_detail.html", learning=learning)

@app.route("/blog")
async def public_blog_list():
    blogs = await SupabaseService.get_skills_by_types(["blog", "learning"])
    return render_template("blog_list.html", blogs=blogs)

@app.route("/achievements")
async def public_achievement_list():
    achievements = await SupabaseService.get_achievements()
    return render_template("achievement_list.html", achievements=achievements)

@app.route("/contact", methods=["POST"])
async def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if name and email and message:
        await SupabaseService.add_contact_message(name, email, message)
        flash("Message received! Thank you.", "success")
    return redirect(url_for("public_index") + "#contact")

# ---------------------------------------------------------------------------
# SMTP Resume Delivery
# ---------------------------------------------------------------------------
def _send_email_sync(user_email):
    """Synchronous email sending (runs in a thread to avoid blocking)."""
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    if not sender_email or not sender_password:
        return False, "Mail config missing"

    msg = MIMEMultipart()
    msg["From"] = f"Darshan Kumar <{sender_email}>"
    msg["To"] = user_email
    msg["Subject"] = "Resume — Darshan Kumar"
    msg.attach(MIMEText(
        "Hello,\n\nPlease find the requested resume attached.\n\nBest,\nDarshan",
        "plain",
    ))

    pdf_path = os.path.join(BASE_DIR, "Darshan kumar r.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "Success"
    except Exception as e:
        return False, str(e)

@app.route("/send_resume", methods=["POST"])
async def send_resume():
    user_email = request.form.get("email")
    if user_email:
        success, error = await asyncio.to_thread(_send_email_sync, user_email)
        if success:
            flash(f"Resume sent to {user_email}", "success")
        else:
            flash(f"Error: {error}", "danger")
    return redirect(url_for("public_index") + "#contact")

# ---------------------------------------------------------------------------
# Local dev server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
