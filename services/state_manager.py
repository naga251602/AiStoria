# services/state_manager.py
from flask import session
from engine.dataframe import DataFrame
from models import Table

def get_dataframe(table_name):
    """
    Factory function to get a DataFrame object.
    Fetches metadata from PostgreSQL based on the active project.
    """
    active_project_id = session.get('active_project_id')
    if not active_project_id:
        return None

    # Query Postgres for the table info
    table_record = Table.query.filter_by(project_id=active_project_id, name=table_name).first()
    
    if table_record:
        try:
            # Re-create the DataFrame object from the stored path
            df = DataFrame(source=table_record.filepath)
            return df
        except Exception as e:
            print(f"Error initializing DataFrame for {table_name}: {e}")
            return None
    
    return None

def clear_cache_for_user():
    """
    No longer needed since we don't cache objects, 
    but kept for interface compatibility.
    """
    pass