# iCash Supermarket System

A microservices-based cash register system for supermarkets, built with Python, Flask, PostgreSQL, and Docker.

## Features

- **Multi-service architecture** with API Gateway
- **Cash Register Service** for recording purchases
- **Analytics Service** for business insights
- **PostgreSQL database** with automatic data loading
- **Docker Compose** for easy deployment

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           API Gateway (Port 8000)                    │
│                                                                     │
│  ┌──────────────────────┐         ┌──────────────────────┐        │
│  │  /cash-register/*    │         │    /analytics/*      │        │
│  └──────────┬───────────┘         └──────────┬───────────┘        │
└─────────────┼──────────────────────────────────┼───────────────────┘
              │                                  │
              ▼                                  ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  Cash Register Service  │         │   Analytics Service     │
│      (Port 8001)       │         │      (Port 8002)       │
└───────────┬─────────────┘         └───────────┬─────────────┘
            │                                   │
            └──────────────┬────────────────────┘
                          ▼
             ┌─────────────────────────┐
             │   PostgreSQL Database   │
             │      (Port 5432)       │
             └─────────────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- Git
- Python 3.11 (for local development)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/morsimha/icash-supermarket.git
cd icash-supermarket
```

2. Start the services:
```bash
docker-compose up -d
```

3. Wait for services to initialize (about 20 seconds)

4. Check service health:
```bash
curl http://localhost:8000/health
```

## Business Requirements (Version 1.0)

### Application A - Cash Register
- Records purchases from 3 supermarket branches (IDs: 1, 2, 3)
- Manages 10 products catalog
- Supports new and returning customers
- Calculates total purchase amount
- Maximum 1 unit per product per purchase

### Application B - Analytics
- Shows count of unique customers across the network
- Lists loyal customers (customers with 3+ purchases)
- Displays top 3 best-selling products (handles ties)

## API Endpoints

### API Gateway (Port 8000)

- `GET /` - API documentation
- `GET /health` - System health check
- `GET /dashboard` - Combined analytics dashboard

### Cash Register Endpoints

- `GET /cash-register/products` - List all products
- `POST /cash-register/purchase` - Record a purchase
- `GET /cash-register/customers` - List existing customers

### Analytics Endpoints

- `GET /analytics/unique-customers` - Count of unique customers
- `GET /analytics/loyal-customers` - List loyal customers (3+ purchases)
- `GET /analytics/top-products` - Top 3 best-selling products
- `GET /analytics/statistics` - Comprehensive statistics

## Example Purchase Request

```json
POST http://localhost:8000/cash-register/purchase

{
    "supermarket_id": 1,
    "user_id": "new",
    "items": [
        {"product_id": 1},
        {"product_id": 3},
        {"product_id": 5}
    ]
}
```

Response:
```json
{
    "purchase_id": 123,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "total_amount": 45.50,
    "items": [
        {"product_id": 1, "name": "Milk", "price": 12.50, "quantity": 1},
        {"product_id": 3, "name": "Eggs", "price": 15.00, "quantity": 1},
        {"product_id": 5, "name": "Yogurt", "price": 6.50, "quantity": 1}
    ]
}
```

## Project Structure

```
icash-supermarket/
├── docker-compose.yml
├── README.md
├── .gitignore
├── database/
│   ├── init.sql
│   └── data/
│       ├── products_list.csv
│       └── purchases.csv
├── cash-register-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── analytics-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── api-gateway/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```

## CSV Data Format

### products_list.csv
```csv
product_name,unit_price
milk,1.5
bread,2
eggs,3
```

### purchases.csv
```csv
supermarket_id,timestamp,user_id,items_list,total_amount
SMKT001,2025-05-26T19:51:00,550e8400-e29b-41d4-a716-446655440001,"eggs,milk",4.5
```

## Testing

Test the system using the provided PowerShell script:
```powershell
.\test-system.ps1
```

Or manually with curl:
```bash
# Get products
curl http://localhost:8000/cash-register/products

# Create purchase
curl -X POST http://localhost:8000/cash-register/purchase \
  -H "Content-Type: application/json" \
  -d '{"supermarket_id": 1, "user_id": "new", "items": [{"product_id": 1}]}'

# Get analytics
curl http://localhost:8000/analytics/unique-customers
curl http://localhost:8000/analytics/loyal-customers
curl http://localhost:8000/analytics/top-products
```

## Monitoring

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f cash-register
```

## Troubleshooting

### Services returning 404 errors
Rebuild the containers to ensure they have the latest code:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection issues
Check if PostgreSQL is healthy:
```bash
docker ps | grep postgres
```

### Port conflicts
Ensure ports 8000, 8001, 8002, and 5432 are not in use by other applications.

## Optional Web UI

An interactive web interface is available in the `ui/` directory:

### Features
- 🛒 Cash Register Interface - Visual purchase creation
- 📊 Real-time Analytics Dashboard
- 👥 Customer Management
- 🇮🇱 Hebrew RTL support

### Usage
1. Ensure Docker services are running
2. Open `ui/index.html` in your browser
3. The UI connects to the API at `http://localhost:8000`

### UI Capabilities
- Select products visually
- Switch between new/existing customers
- View analytics in real-time
- Create test purchases easily

*Note: The UI is optional and not required for the core system functionality.*

## Technologies Used

- **Python 3.11** - Programming language
- **Flask** - Web framework
- **PostgreSQL** - Database
- **Docker & Docker Compose** - Containerization
- **psycopg2** - PostgreSQL adapter for Python
- **HTML/CSS/JavaScript** - Optional web UI

## Author

Mor Simha