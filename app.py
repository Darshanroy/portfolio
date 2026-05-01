import os
import asyncio
import smtplib
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

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")

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

@app.route("/")
async def public_index():
    try:
        # High-Speed Parallel Fetching
        # Now extremely fast as it uses the Data Store by default
        projects, skills, blogs, achievements = await asyncio.gather(
            SupabaseService.get_projects(),
            SupabaseService.get_skills(skill_type="skill"),
            SupabaseService.get_skills_by_types(["blog", "learning"]),
            SupabaseService.get_achievements()
        )

        return render_template(
            "public/index.html",
            projects=projects,
            skills=skills,
            blogs=blogs,
            achievements=achievements,
        )
    except Exception as e:
        if os.environ.get("VERCEL"):
            return f"<h1>Service Temporarily Unavailable</h1><p>{str(e)}</p>", 500
        raise e

@app.route("/project/<project_id>")
async def public_project_detail(project_id):
    project = await SupabaseService.get_project(project_id)
    if not project:
        abort(404)
    return render_template("public/project_detail.html", project=project)

@app.route("/learning/<learning_id>")
async def public_learning_detail(learning_id):
    learning = await SupabaseService.get_skill_with_sections(learning_id)
    if not learning:
        abort(404)
    return render_template("public/learning_detail.html", learning=learning)

@app.route("/blog")
async def public_blog_list():
    blogs = await SupabaseService.get_skills_by_types(["blog", "learning"])
    return render_template("public/blog_list.html", blogs=blogs)

@app.route("/achievements")
async def public_achievement_list():
    achievements = await SupabaseService.get_achievements()
    return render_template("public/achievement_list.html", achievements=achievements)

@app.route("/contact", methods=["POST"])
async def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if name and email and message:
        # Async background push to Supabase
        await SupabaseService.add_contact_message(name, email, message)
        flash("Message received! Thank you.", "success")
    return redirect(url_for("public_index") + "#contact")

def _send_email_sync(user_email):
    """Synchronous email sending logic."""
    sender_email = os.environ.get("MAIL_USERNAME")
    sender_password = os.environ.get("MAIL_PASSWORD")
    if not sender_email or not sender_password: return False, "Config error"

    msg = MIMEMultipart()
    msg['From'] = f"Darshan Kumar <{sender_email}>"
    msg['To'] = user_email
    msg['Subject'] = "Resume Request - Darshan Kumar"
    msg.attach(MIMEText("Hello,\n\nPlease find the requested resume attached.\n\nBest,\nDarshan", 'plain'))

    pdf_path = os.path.join(os.path.dirname(__file__), "Darshan kumar r.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "Success"
    except Exception as e: return False, str(e)

@app.route("/send_resume", methods=["POST"])
async def send_resume():
    user_email = request.form.get("email")
    if user_email:
        success, error = await asyncio.to_thread(_send_email_sync, user_email)
        if success: flash(f"Resume sent to {user_email}", "success")
        else: flash(f"Error: {error}", "danger")
    return redirect(url_for("public_index") + "#contact")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
