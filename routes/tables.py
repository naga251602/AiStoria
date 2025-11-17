# routes/tables.py
import os
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Table, Project

tables_bp = Blueprint('tables', __name__)

def get_table_if_owner(table_id, user_id):
    """Security check: Ensures the user owns the table."""
    table = Table.query.get(table_id)
    if not table:
        return None
    project = Project.query.get(table.project_id)
    if project.user_id != user_id:
        return None
    return table

@tables_bp.route('/api/tables/<int:id>', methods=['PUT'])
def rename_table(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    table = get_table_if_owner(id, user_id)
    if not table:
        return jsonify({'success': False, 'error': 'Table not found'}), 404

    data = request.get_json()
    new_name = data.get('name')
    if not new_name:
        return jsonify({'success': False, 'error': 'Name is required'}), 400
    
    # Check for name collision in the same project
    exists = Table.query.filter_by(project_id=table.project_id, name=new_name).first()
    if exists:
        return jsonify({'success': False, 'error': 'A table with this name already exists'}), 409
    
    table.name = new_name
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Table renamed'})

@tables_bp.route('/api/tables/<int:id>', methods=['DELETE'])
def delete_table(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    table = get_table_if_owner(id, user_id)
    if not table:
        return jsonify({'success': False, 'error': 'Table not found'}), 404

    try:
        # 1. Delete the physical file
        if os.path.exists(table.filepath):
            os.remove(table.filepath)
        
        # 2. Delete the DB record
        db.session.delete(table)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Table deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500