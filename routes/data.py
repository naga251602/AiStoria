# routes/data.py
import os
from flask import Blueprint, request, jsonify, session, current_app
from extensions import db
from models import Table, Project
from engine.dataframe import DataFrame

data_bp = Blueprint('data', __name__)

@data_bp.route('/api/upload', methods=['POST'])
def upload_files():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
        
    active_project_id = session.get('active_project_id')
    if not active_project_id:
        return jsonify({'success': False, 'error': 'No database selected'}), 400

    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files part'}), 400

    files = request.files.getlist('files')
    schema_cache = session.get('db_schema', {})

    for file in files:
        try:
            filename = file.filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            df = DataFrame(source=filepath)
            column_types = df.get_column_types()
            row_count = len(df)
            
            table_name = os.path.splitext(filename)[0]
            
            new_table = Table(
                name=table_name,
                filename=filename,
                filepath=filepath,
                columns_schema=column_types,
                row_count=row_count,
                project_id=active_project_id
            )
            db.session.add(new_table)
            db.session.commit()
            
            schema_cache[table_name] = {
                'id': new_table.id,
                'filename': filename,
                'types': column_types,
                'row_count': row_count
            }

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    session['db_schema'] = schema_cache
    return jsonify({'success': True, 'schema': schema_cache})