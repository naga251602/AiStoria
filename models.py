# models.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tables = db.relationship('Table', backref='project', lazy=True, cascade="all, delete-orphan")

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    columns_schema = db.Column(db.JSON, nullable=True) 
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    row_count = db.Column(db.Integer)