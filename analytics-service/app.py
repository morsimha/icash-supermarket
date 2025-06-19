import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 8002))

def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "analytics"}), 200

@app.route('/unique-customers', methods=['GET'])
def get_unique_customers():
    """Get count of unique customers across the network"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(DISTINCT user_id) as unique_customers FROM purchases")
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            "unique_customers": result['unique_customers']
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/loyal-customers', methods=['GET'])
def get_loyal_customers():
    """Get list of loyal customers (3+ purchases)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                user_id,
                COUNT(*) as purchase_count,
                SUM(total_amount) as total_spent,
                MIN(timestamp) as first_purchase,
                MAX(timestamp) as last_purchase
            FROM purchases
            GROUP BY user_id
            HAVING COUNT(*) >= 3
            ORDER BY purchase_count DESC, total_spent DESC
        """)
        
        loyal_customers = cur.fetchall()
        
        # Convert Decimal to float for JSON serialization
        for customer in loyal_customers:
            customer['total_spent'] = float(customer['total_spent'])
            customer['first_purchase'] = customer['first_purchase'].isoformat()
            customer['last_purchase'] = customer['last_purchase'].isoformat()
        
        cur.close()
        conn.close()
        
        return jsonify({
            "loyal_customers_count": len(loyal_customers),
            "loyal_customers": loyal_customers
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/top-products', methods=['GET'])
def get_top_products():
    """Get top 3 best-selling products of all time"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Extract product sales from JSONB items_list
        cur.execute("""
            WITH product_sales AS (
                SELECT 
                    (item->>'product_id')::INTEGER as product_id,
                    item->>'name' as product_name,
                    COUNT(*) as units_sold
                FROM purchases,
                     jsonb_array_elements(items_list) as item
                GROUP BY product_id, product_name
            )
            SELECT 
                product_id,
                product_name,
                units_sold,
                RANK() OVER (ORDER BY units_sold DESC) as rank
            FROM product_sales
            ORDER BY units_sold DESC
        """)
        
        all_products = cur.fetchall()
        
        # Get top 3 ranks (may include more than 3 products if there are ties)
        top_products = [p for p in all_products if p['rank'] <= 3]
        
        cur.close()
        conn.close()
        
        return jsonify({
            "top_products": top_products
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all statistics in one endpoint
        stats = {}
        
        # Unique customers
        cur.execute("SELECT COUNT(DISTINCT user_id) as count FROM purchases")
        stats['unique_customers'] = cur.fetchone()['count']
        
        # Total purchases
        cur.execute("SELECT COUNT(*) as count FROM purchases")
        stats['total_purchases'] = cur.fetchone()['count']
        
        # Total revenue
        cur.execute("SELECT SUM(total_amount) as total FROM purchases")
        total_revenue = cur.fetchone()['total']
        stats['total_revenue'] = float(total_revenue) if total_revenue else 0
        
        # Purchases by supermarket
        cur.execute("""
            SELECT 
                supermarket_id,
                COUNT(*) as purchase_count,
                SUM(total_amount) as revenue
            FROM purchases
            GROUP BY supermarket_id
            ORDER BY supermarket_id
        """)
        
        stats['by_supermarket'] = []
        for row in cur.fetchall():
            stats['by_supermarket'].append({
                'supermarket_id': row['supermarket_id'],
                'purchase_count': row['purchase_count'],
                'revenue': float(row['revenue'])
            })
        
        cur.close()
        conn.close()
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)