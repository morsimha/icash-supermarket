import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Service URLs from environment
CASH_REGISTER_URL = os.environ.get('CASH_REGISTER_URL', 'http://localhost:8001')
ANALYTICS_URL = os.environ.get('ANALYTICS_URL', 'http://localhost:8002')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 8000))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "api-gateway"}), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "service": "iCash API Gateway",
        "version": "1.0",
        "endpoints": {
            "health": "GET /health",
            "dashboard": "GET /dashboard",
            "cash_register": {
                "products": "GET /cash-register/products",
                "purchase": "POST /cash-register/purchase"
            },
            "analytics": {
                "unique_customers": "GET /analytics/unique-customers",
                "loyal_customers": "GET /analytics/loyal-customers"
            }
        }
    }), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Simple dashboard endpoint"""
    return jsonify({"message": "Dashboard endpoint", "status": "ok"}), 200

if __name__ == '__main__':
    print(f"Starting API Gateway on port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
