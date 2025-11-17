# services/chart_builder.py
import json
import urllib.parse

def build_chart_url(title, chart_type, data):
    """
    Takes aggregation data and builds a QuickChart URL.
    """
    if not data:
        return None
    
    try:
        labels = list(data.keys())
        # Get the first aggregation key
        first_data_row = list(data.values())[0]
        data_key = list(first_data_row.keys())[0]
        dataset_label = data_key
        
        # Get the data
        chart_data = [float(row[data_key]) for row in data.values()]
        
        chart_config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': dataset_label,
                    'data': chart_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                    'borderColor': 'rgba(54, 162, 235, 1)'
                }]
            },
            'options': {
                'title': { 'display': True, 'text': title }
            }
        }

        config_json = json.dumps(chart_config)
        encoded_config = urllib.parse.quote(config_json)
        return f"https://quickchart.io/chart?c={encoded_config}"
    except Exception as e:
        print(f"Error building chart: {e}")
        return None