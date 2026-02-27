from flask import Flask, jsonify, request, render_template, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
from tinydb import TinyDB, Query # type: ignore
from datetime import datetime
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# Enable CORS for development and API routes
CORS(app)

# Initialize TinyDB JSON database
db_path = os.path.join(os.path.dirname(__file__), 'sensor_data.json')

def get_db():
    """Safely get the database instance, resetting it if corrupted."""
    try:
        db = TinyDB(db_path)
        # Try a test operation to check for corruption
        db.all()
        return db
    except Exception as e:
        print(f"Database corrupted, resetting: {e}")
        if os.path.exists(db_path):
            os.remove(db_path)
        return TinyDB(db_path)

@app.route('/')
def serve_dashboard():
    """Serve the main dashboard HTML file."""
    return send_from_directory('.', 'react_dashboard.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to avoid 404 logs."""
    return '', 204

@app.route('/api/readings', methods=['GET'])
def get_readings():
    """Get the latest sensor readings for the dashboard."""
    db = get_db()
    limit = int(request.args.get('limit', 50))
    # TinyDB returns all records as a list of dicts
    all_readings = db.all()
    
    # Sort by reading_time descending (latest first)
    # If reading_time is missing, use empty string as fallback
    sorted_readings = sorted(
        all_readings, 
        key=lambda x: x.get('reading_time', ''), 
        reverse=True
    )
    
    latest_readings = sorted_readings[:limit]
    
    return jsonify({
        'readings': list(reversed(latest_readings)), # Return in chronological order for charts
        'latest': sorted_readings[0] if sorted_readings else None,
        'count': len(all_readings)
    })

@app.route('/test_data.php', methods=['POST'])
@app.route('/api/add', methods=['POST'])
def add_reading():
    """
    Handle sensor data from Arduino or test scripts.
    Supports both JSON and Form data for compatibility with existing Arduino code.
    """
    db = get_db()
    # Check if data is form-encoded (Arduino style) or JSON
    if request.is_json:
        data = request.json
    else:
        # request.form handles application/x-www-form-urlencoded
        data = request.form.to_dict()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Prepare the reading record
    reading = {
        'temperature': float(data.get('temperature', 0)),
        'humidity': float(data.get('humidity', 0)),
        'light': float(data.get('light', 0)),
        'voltage': float(data.get('voltage', 0)),
        'current': float(data.get('current', 0)),
        'reading_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    db.insert(reading)
    print(f"Recorded reading: {reading}")
    return jsonify({'status': 'success', 'data': reading}), 201

@app.route('/delete_data.php', methods=['POST'])
@app.route('/api/delete', methods=['POST'])
def delete_data():
    """Clear all sensor data from the JSON database."""
    db = get_db()
    db.truncate()
    return jsonify({'status': 'success', 'message': 'All data deleted'})

if __name__ == '__main__':
    # Development server
    print("Starting Sensor Dashboard Backend...")
    print(f"JSON Database location: {db_path}")
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Production configuration (for PythonAnywhere)
    print("Running in production mode")
