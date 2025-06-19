import os
import json
import uuid
from datetime import datetime
from decimal import Decimal
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 8001))

def get_db_connection():
    """Create and return a database connection"""
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "cash-register"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    """Get all available products"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        cur = conn.cursor()
        cur.execute("SELECT id, name, price FROM products ORDER BY id")
        products = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Convert Decimal to float for JSON serialization
        for product in products:
            product['price'] = float(product['price'])
        
        return jsonify(products), 200
    except Exception as e:
        print(f"Error in get_products: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/purchase', methods=['POST'])
def create_purchase():
    """Record a new purchase"""
    return jsonify({"message": "Purchase endpoint", "status": "ok"}), 200

if __name__ == '__main__':
    print(f"Starting Cash Register Service on port {SERVICE_PORT}")
    print(f"Database URL: {DATABASE_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
