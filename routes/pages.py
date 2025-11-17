# routes/pages.py
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    return render_template('index.html')

@pages_bp.route('/app')
def app_page():
    return render_template('app.html')