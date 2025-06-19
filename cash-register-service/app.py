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
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "cash-register"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    """Get all available products"""
    try:
        conn = get_db_connection()
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
        return jsonify({"error": str(e)}), 500

@app.route('/purchase', methods=['POST'])
def create_purchase():
    """Record a new purchase"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['supermarket_id', 'user_id', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate supermarket_id (1-3)
        if data['supermarket_id'] not in [1, 2, 3]:
            return jsonify({"error": "Invalid supermarket_id. Must be 1, 2, or 3"}), 400
        
        # Generate new user_id if needed
        if data['user_id'] == 'new':
            user_id = str(uuid.uuid4())
        else:
            user_id = data['user_id']
        
        # Calculate total amount
        conn = get_db_connection()
        cur = conn.cursor()
        
        total_amount = Decimal('0')
        items_with_details = []
        
        for item in data['items']:
            cur.execute("SELECT id, name, price FROM products WHERE id = %s", (item['product_id'],))
            product = cur.fetchone()
            
            if not product:
                cur.close()
                conn.close()
                return jsonify({"error": f"Product with id {item['product_id']} not found"}), 400
            
            # Each customer can buy only one unit per product
            quantity = 1
            item_total = product['price'] * quantity
            total_amount += item_total
            
            items_with_details.append({
                "product_id": product['id'],
                "name": product['name'],
                "price": float(product['price']),
                "quantity": quantity
            })
        
        # Insert purchase record
        cur.execute("""
            INSERT INTO purchases (supermarket_id, timestamp, user_id, items_list, total_amount)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['supermarket_id'],
            datetime.now(),
            user_id,
            json.dumps(items_with_details),
            total_amount
        ))
        
        purchase_id = cur.fetchone()['id']
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "purchase_id": purchase_id,
            "user_id": user_id,
            "total_amount": float(total_amount),
            "items": items_with_details
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customers', methods=['GET'])
def get_existing_customers():
    """Get list of existing customers for simulation"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT user_id, COUNT(*) as purchase_count
            FROM purchases
            GROUP BY user_id
            ORDER BY purchase_count DESC
            LIMIT 20
        """)
        
        customers = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify(customers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)