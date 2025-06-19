import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Service URLs
CASH_REGISTER_URL = os.environ.get('CASH_REGISTER_URL')
ANALYTICS_URL = os.environ.get('ANALYTICS_URL')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 8000))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    services_health = {}
    
    # Check Cash Register Service
    try:
        response = requests.get(f"{CASH_REGISTER_URL}/health", timeout=5)
        services_health['cash_register'] = response.status_code == 200
    except:
        services_health['cash_register'] = False
    
    # Check Analytics Service
    try:
        response = requests.get(f"{ANALYTICS_URL}/health", timeout=5)
        services_health['analytics'] = response.status_code == 200
    except:
        services_health['analytics'] = False
    
    all_healthy = all(services_health.values())
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "services": services_health
    }), 200 if all_healthy else 503

# Cash Register Service Routes
@app.route('/cash-register/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_cash_register(path):
    """Proxy requests to Cash Register Service"""
    try:
        url = f"{CASH_REGISTER_URL}/{path}"
        
        if request.method == 'GET':
            response = requests.get(url, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url)
        
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": f"Cash Register Service error: {str(e)}"}), 503

# Analytics Service Routes
@app.route('/analytics/<path:path>', methods=['GET'])
def proxy_analytics(path):
    """Proxy requests to Analytics Service"""
    try:
        url = f"{ANALYTICS_URL}/{path}"
        response = requests.get(url, params=request.args)
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": f"Analytics Service error: {str(e)}"}), 503

# Combined Dashboard Endpoint
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Get all analytics data for dashboard"""
    try:
        data = {}
        
        # Get unique customers
        response = requests.get(f"{ANALYTICS_URL}/unique-customers")
        if response.status_code == 200:
            data['unique_customers'] = response.json()['unique_customers']
        
        # Get loyal customers
        response = requests.get(f"{ANALYTICS_URL}/loyal-customers")
        if response.status_code == 200:
            loyal_data = response.json()
            data['loyal_customers_count'] = loyal_data['loyal_customers_count']
            data['loyal_customers'] = loyal_data['loyal_customers'][:10]  # Top 10
        
        # Get top products
        response = requests.get(f"{ANALYTICS_URL}/top-products")
        if response.status_code == 200:
            data['top_products'] = response.json()['top_products']
        
        # Get statistics
        response = requests.get(f"{ANALYTICS_URL}/statistics")
        if response.status_code == 200:
            data['statistics'] = response.json()
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
                "purchase": "POST /cash-register/purchase",
                "customers": "GET /cash-register/customers"
            },
            "analytics": {
                "unique_customers": "GET /analytics/unique-customers",
                "loyal_customers": "GET /analytics/loyal-customers",
                "top_products": "GET /analytics/top-products",
                "statistics": "GET /analytics/statistics"
            }
        }
    }), 200

if __name__ == '__main__':
    print(f"Starting API Gateway on port {SERVICE_PORT}")
    print(f"Cash Register URL: {CASH_REGISTER_URL}")
    print(f"Analytics URL: {ANALYTICS_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)