# routes/databases.py
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Project, Table

databases_bp = Blueprint('databases', __name__)

@databases_bp.route('/api/databases', methods=['GET'])
def get_databases():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    projects = Project.query.filter_by(user_id=session['user_id']).all()
    return jsonify({
        'success': True, 
        'databases': [{'id': p.id, 'name': p.name, 'table_count': len(p.tables)} for p in projects]
    })

@databases_bp.route('/api/databases', methods=['POST'])
def create_database():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'Name required'}), 400

    new_project = Project(name=name, user_id=session['user_id'])
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({'success': True, 'database': {'id': new_project.id, 'name': new_project.name}})

@databases_bp.route('/api/databases/<int:id>', methods=['PUT'])
def rename_database(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    project = Project.query.filter_by(id=id, user_id=session['user_id']).first()
    if not project:
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    data = request.get_json()
    project.name = data.get('name', project.name)
    db.session.commit()
    
    return jsonify({'success': True})

@databases_bp.route('/api/databases/<int:id>', methods=['DELETE'])
def delete_database(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    project = Project.query.filter_by(id=id, user_id=session['user_id']).first()
    if not project:
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    # The `cascade` in models.py will auto-delete all tables
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'success': True})

@databases_bp.route('/api/databases/select', methods=['POST'])
def select_database():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    project_id = data.get('id')
    
    project = Project.query.filter_by(id=project_id, user_id=session['user_id']).first()
    if not project:
        return jsonify({'success': False, 'error': 'Database not found'}), 404
        
    session['active_project_id'] = project.id
    
    # Load schema for the frontend
    schema = {}
    for table in project.tables:
        schema[table.name] = {
            'id': table.id,
            'filename': table.filename,
            'types': table.columns_schema,
            'row_count': table.row_count
        }
    
    session['db_schema'] = schema # For chat/upload routes
    return jsonify({'success': True, 'schema': schema, 'name': project.name})