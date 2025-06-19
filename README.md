A microservices-based cash register system for supermarkets, built with Python, Flask, PostgreSQL, and Docker.

## Features

- **Multi-service architecture** with API Gateway
- **Cash Register Service** for recording purchases
- **Analytics Service** for business insights
- **PostgreSQL database** with automatic data loading
- **Docker Compose** for easy deployment

## Prerequisites

- Docker and Docker Compose installed
- Git
- Python 3.11 (for local development)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/icash-supermarket.git
cd icash-supermarket

Place your CSV files in the database/data/ directory:

products_list.csv - Product catalog
purchases.csv - Historical purchases


Start the services:

bashdocker-compose up -d

Check service health:

bashcurl http://localhost:8000/health
API Endpoints
API Gateway (Port 8000)

GET / - API documentation
GET /health - System health check
GET /dashboard - Combined analytics dashboard

Cash Register Endpoints

GET /cash-register/products - List all products
POST /cash-register/purchase - Record a purchase
GET /cash-register/customers - List existing customers

Analytics Endpoints

GET /analytics/unique-customers - Count of unique customers
GET /analytics/loyal-customers - List loyal customers (3+ purchases)
GET /analytics/top-products - Top 3 best-selling products
GET /analytics/statistics - Comprehensive statistics

Example Purchase Request
jsonPOST http://localhost:8000/cash-register/purchase

{
    "supermarket_id": 1,
    "user_id": "new",
    "items": [
        {"product_id": 1},
        {"product_id": 3},
        {"product_id": 5}
    ]
}
Architecture

API Gateway: Central entry point, routes requests to appropriate services
Cash Register Service: Handles purchase transactions
Analytics Service: Provides business insights and reports
PostgreSQL Database: Stores products and purchases data

Development
To run services individually for development:

Start PostgreSQL:

bashdocker-compose up -d postgres

Run services locally:

bash# Terminal 1 - Cash Register Service
cd cash-register-service
pip install -r requirements.txt
export DATABASE_URL=postgresql://icash_user:icash_password@localhost:5432/icash_db
python app.py

# Terminal 2 - Analytics Service
cd analytics-service
pip install -r requirements.txt
export DATABASE_URL=postgresql://icash_user:icash_password@localhost:5432/icash_db
python app.py

# Terminal 3 - API Gateway
cd api-gateway
pip install -r requirements.txt
export CASH_REGISTER_URL=http://localhost:8001
export ANALYTICS_URL=http://localhost:8002
python app.py
Testing
Test the system using curl or any HTTP client:
bash# Get products
curl http://localhost:8000/cash-register/products

# Create purchase
curl -X POST http://localhost:8000/cash-register/purchase \
  -H "Content-Type: application/json" \
  -d '{"supermarket_id": 1, "user_id": "new", "items": [{"product_id": 1}]}'

# Get analytics
curl http://localhost:8000/dashboard
Monitoring
View logs:
bash# All services
docker-compose logs -f

# Specific service
docker-compose logs -f cash-register
Shutdown
Stop all services:
bashdocker-compose down

# Remove volumes (careful - deletes data!)
docker-compose down -v
