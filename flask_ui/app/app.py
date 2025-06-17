from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": query,
                "max_results": max_results
            },
            timeout=300
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to API server"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "ui_status": "healthy",
                "api_status": response.json()
            })
        else:
            return jsonify({
                "ui_status": "healthy",
                "api_status": "unhealthy"
            }), 503
    except:
        return jsonify({
            "ui_status": "healthy",
            "api_status": "unreachable"
        }), 503

@app.route('/stats')
def stats():
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get stats"}), 500
    except:
        return jsonify({"error": "Cannot connect to API server"}), 503

if __name__ == '__main__':
    app.run(debug=True, port=5000)