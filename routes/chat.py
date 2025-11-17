# routes/chat.py
import json
import re
from flask import Blueprint, request, jsonify, session
from services.llm_service import get_model
from services.state_manager import get_dataframe
from services.chart_builder import build_chart_url
from services.security import secure_eval, SecurityViolation
from services.logger import get_logger

chat_bp = Blueprint('chat', __name__)
logger = get_logger(__name__)

@chat_bp.route('/api/detect-relationships', methods=['POST'])
def detect_relationships():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
    model = get_model()
    if not model:
        return jsonify({'success': False, 'error': 'AI model not configured'}), 500
        
    schema = session.get('db_schema', {})
    if len(schema) < 2:
        return jsonify({'success': False, 'error': 'At least two tables are required.'}), 400

    prompt_schema = {name: details['types'] for name, details in schema.items()}
    
    prompt = f"""
    You are an expert database administrator. Given this schema:
    {json.dumps(prompt_schema)}
    Analyze and infer foreign key relationships. Return ONLY a JSON object:
    {{ "success": true, "relationships": [ {{ "from_table": "t1", "from_column": "c1", "to_table": "t2", "to_column": "c2" }} ] }}
    """

    try:
        response = model.generate_content(prompt)
        # Clean logic for JSON response
        json_str = response.text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        elif json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        result = json.loads(json_str.strip())
        session['db_relationships'] = result.get('relationships', [])
        
        logger.info(f"Relationships detected: {len(result.get('relationships', []))}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in Gemini relationship detection: {e}")
        return jsonify({'success': False, 'error': f'AI API Error: {str(e)}'}), 500

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'type': 'error', 'data': 'Unauthorized.'}), 401
        
    model = get_model()
    if not model:
        return jsonify({'type': 'error', 'data': 'AI model not configured'}), 500

    data = request.get_json()
    user_query = data.get('query')
    schema = session.get('db_schema', {})
    relationships = session.get('db_relationships', [])
    
    if not schema:
        return jsonify({'type': 'error', 'data': 'No database schema found.'}), 400

    # 1. Prepare Schema & Tables
    prompt_schema = {name: details['types'] for name, details in schema.items()}
    table_definitions = "\n".join([f"{name} = get_dataframe('{name}')" for name in schema.keys()])
    
    relationship_info = "No known relationships."
    if relationships:
        relationship_info = '\n'.join([f"{r['from_table']}.{r['from_column']} -> {r['to_table']}.{r['to_column']}" for r in relationships])

    # 2. Robust Prompt with all fixes
    prompt = f"""
    You are a data analysis bot. You have access to a custom Python DataFrame library.

    --- DATABASE SCHEMA ---
    {json.dumps(prompt_schema, indent=2)}

    --- AVAILABLE PYTHON OBJECTS ---
    {table_definitions}
    
    --- METHODS & PROPERTIES ---
    - len(df) -> int
    - .filter(lambda row: condition) -> DataFrame
    - .project(list_of_cols) -> list[dict]
    - .join(other_df, left_col, right_col) -> DataFrame
    - .groupby(col_name) -> dict
    - .aggregate(groups, {{col: func}}) -> dict
        - Supported funcs: 'count', 'sum', 'avg', 'min', 'max'
    - .columns -> list[str] (This is a property, NOT a function)
    - build_chart_url(title, type, data) -> str
        - `data` MUST be the RAW dictionary returned by .aggregate().
    
    --- CRITICAL RULES ---
    1.  **OUTPUT FORMAT:** Return JSON: {{ "isCode": boolean, "content": string }}.
    2.  **TABLE OUTPUT:** To show a table, you MUST use `.project()`. To show ALL columns, use `df.columns` (e.g., `customers.project(customers.columns)[:10]`). You MUST slice the result (e.g., `[:10]`).
    3.  **CHARTING:** When using `build_chart_url`, pass the result of `.aggregate()` DIRECTLY as the 3rd argument.
    4.  **DATA TYPES:** Cast numbers when filtering (e.g., `int(row['age']) > 30`).
    5.  **TABLE NAMES:** Use exact variable names.
    6.  **FORBIDDEN:** Do NOT use `list()` or `.keys()`. Use `.columns`.
    
    --- EXAMPLES ---
    User: "Hello"
    Response: {{ "isCode": false, "content": "Hello! I am ready to analyze your data." }}

    User: "How many students?" 
    Response: {{ "isCode": true, "content": "len(students)" }}
    
    User: "show me the first 10 customers"
    Response: {{ "isCode": true, "content": "customers.project(customers.columns)[:10]" }}

    User: "Show me 3 orders"
    Response: {{ "isCode": true, "content": "orders.project(orders.columns)[:3]" }}

    User: "Plot a bar chart of sales by country"
    Response: {{ "isCode": true, "content": "build_chart_url('Sales by Country', 'bar', customers.join(orders, 'customer_id', 'customer_id').aggregate(customers.join(orders, 'customer_id', 'customer_id').groupby('country'), {{'total_amount': 'sum'}}))" }}

    NOW, generate the JSON for: "{user_query}"
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean Markdown
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        ai_response = json.loads(response_text.strip())
        
        if not ai_response.get('isCode'):
            return jsonify({'type': 'text', 'data': ai_response['content']})
        
        code_to_run = ai_response['content']
        logger.info(f"--- AI-Generated Code ---\n{code_to_run}") # Log the code *before* execution

        # 3. Context
        safe_context = {
            "get_dataframe": get_dataframe,
            "len": len,
            "int": int, "float": float, "str": str,
            "build_chart_url": build_chart_url
        }
        for table_name in schema.keys():
            safe_context[table_name] = get_dataframe(table_name)
        
        result = secure_eval(code_to_run, safe_context)

        # 4. Response Formatting
        if isinstance(result, str) and result.startswith("https://quickchart.io"):
            return jsonify({'type': 'chart', 'data': result, 'query': code_to_run})
        elif isinstance(result, list):
            return jsonify({'type': 'table', 'data': result, 'query': code_to_run})
        elif isinstance(result, dict):
            table_result = []
            group_key_match = re.search(r".groupby\('([^']+)'\)", code_to_run)
            g_key = group_key_match.group(1) if group_key_match else "group"
            for k, v in result.items():
                row = {g_key: k}
                row.update(v)
                table_result.append(row)
            return jsonify({'type': 'table', 'data': table_result, 'query': code_to_run})
        elif isinstance(result, (int, float)):
            return jsonify({'type': 'count', 'data': result, 'query': code_to_run})
        else:
            return jsonify({'type': 'text', 'data': str(result), 'query': code_to_run})

    except SecurityViolation as se:
        logger.warning(f"Security Violation Attempt: {str(se)}")
        return jsonify({'type': 'error', 'data': f"Security Block: {str(se)}", 'query': code_to_run})
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({'type': 'error', 'data': f"Error: {str(e)}", 'query': 'N/A'})