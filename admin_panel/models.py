from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    metrics = db.Column(db.Text)
    architecture = db.Column(db.Text)
    failure_handling = db.Column(db.Text)
    tradeoffs = db.Column(db.Text)
    impact = db.Column(db.Text)
    github_url = db.Column(db.String(255))
    live_url = db.Column(db.String(255))
    chat_url = db.Column(db.String(255))
    images = db.Column(db.Text)  # JSON string of image URLs

    def set_images(self, images_list):
        self.images = json.dumps(images_list)

    def get_images(self):
        return json.loads(self.images) if self.images else []

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'skill', 'learning', 'blog'
    date = db.Column(db.String(50))
    reading_time = db.Column(db.String(50))
    
    sections = db.relationship('SkillSection', backref='skill', lazy=True, cascade="all, delete-orphan")

class SkillSection(db.Model):
    __tablename__ = 'skill_sections'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill_id = db.Column(db.String(50), db.ForeignKey('skills.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    issuer = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(500), nullable=True)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
