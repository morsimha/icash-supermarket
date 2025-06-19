import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "analytics"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('SERVICE_PORT', 8002))
    app.run(host='0.0.0.0', port=port, debug=True)