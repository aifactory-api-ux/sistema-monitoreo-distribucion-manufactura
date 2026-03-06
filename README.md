# sistema-monitoreo-distribucion-manufactura

A comprehensive distribution management dashboard built with React, FastAPI, and SQLite. Monitor KPIs, manage orders, and visualize distribution data with real-time updates.

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (required)
  - Download from [docker.com](https://www.docker.com/products/docker-desktop)
  - Ensure Docker Desktop is running before proceeding

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd distroviz-v3
   ```

2. **Start the application**
   
   **Linux/macOS:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   **Windows:**
   ```cmd
   run.bat
   ```

3. **Access the application**
   - 🌐 **Web Dashboard**: http://localhost:3000
   - 🔧 **API Documentation**: http://localhost:8000/docs
   - ❤️ **Health Check**: http://localhost:8000/api/health

That's it! The application will automatically:
- Build Docker images
- Initialize the database with seed data
- Start all services
- Wait for health checks to pass
- Display access URLs

## 📊 Features

### Dashboard
- **4 Key Performance Indicators (KPIs)**:
  - Total Orders
  - Fulfillment Rate
  - Average Delivery Days
  - Active Plants
- **Interactive Charts**:
  - Order trends over time
  - Distribution by order status
- **Responsive Design**: Optimized for desktop, tablet, and mobile

### Orders Management
- View all orders in a sortable table
- Create new orders with plant and distribution center selection
- Real-time updates without page refresh
- Form validation and error handling

### API Endpoints
- `GET /api/dashboard/summary` - KPI data and metrics
- `GET /api/orders` - List all orders with filtering
- `POST /api/orders` - Create new orders
- `GET /api/plants` - Available plants
- `GET /api/centers` - Distribution centers
- `GET /api/health` - Service health status

## 🏗️ Architecture

### Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic, Uvicorn
- **Database**: SQLite with seed data
- **Infrastructure**: Docker, Docker Compose

### Project Structure
```
distroviz-v3/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript definitions
│   ├── Dockerfile         # Frontend container
│   └── package.json       # Dependencies
├── backend/               # FastAPI service
│   ├── routes/            # API route handlers
│   ├── db/                # Database setup and migrations
│   ├── Dockerfile         # Backend container
│   └── main.py            # Application entry point
├── shared/                # Common utilities
│   ├── models.py          # Database models
│   ├── database.py        # Database configuration
│   └── config.py          # Application settings
├── docs/                  # Documentation
├── data/                  # SQLite database storage
├── docker-compose.yml     # Service orchestration
└── run.sh / run.bat       # Startup scripts
```

## 🛠️ Development

### Environment Configuration

Customize settings by editing `.env` (created from `.env.example`):

```env
# Database
DATABASE_URL=sqlite:///./data/distroviz.db

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Management Commands

```bash
# View service logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Rebuild and restart
./run.sh

# Access backend container
docker compose exec backend bash

# Access frontend container
docker compose exec frontend sh
```

### Database Management

The SQLite database is automatically initialized with:
- **Plants**: 15 sample manufacturing plants
- **Distribution Centers**: 8 regional centers
- **Orders**: 50+ sample orders with various statuses

Database file location: `./data/distroviz.db`

## 🧪 Testing API Endpoints

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Dashboard summary
curl http://localhost:8000/api/dashboard/summary

# List orders
curl http://localhost:8000/api/orders

# Create new order
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "plant_id": 1,
    "distribution_center_id": 1,
    "product_name": "Test Product",
    "quantity": 100,
    "priority": "high"
  }'
```

### Using the API Documentation

Visit http://localhost:8000/docs for interactive API documentation with:
- Request/response schemas
- Try-it-out functionality
- Authentication details
- Example payloads

## 🔧 Troubleshooting

### Common Issues

**Docker not running**
```
[ERROR] Docker is not running
```
- Start Docker Desktop and wait for it to fully initialize
- Verify with `docker --version`

**Port conflicts**
```
[ERROR] Port 3000 is already in use
```
- Stop other services using ports 3000 or 8000
- Or modify ports in `.env` file

**Services not healthy**
```
[WARNING] Services may not be fully healthy yet
```
- Wait a few more minutes for initialization
- Check logs: `docker compose logs -f`
- Restart: `docker compose down && ./run.sh`

### Getting Help

1. **Check service status**: `docker compose ps`
2. **View logs**: `docker compose logs -f [service-name]`
3. **Restart services**: `docker compose restart`
4. **Clean restart**: `docker compose down && ./run.sh`

## 📈 Performance

- **Frontend**: Optimized Vite build with code splitting
- **Backend**: Async FastAPI with connection pooling
- **Database**: Indexed SQLite for fast queries
- **Docker**: Multi-stage builds for minimal image sizes

## 🔒 Security

- No hardcoded credentials (environment variables only)
- CORS protection configured
- Input validation on all endpoints
- Non-root Docker containers
- Health checks for service monitoring

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using modern web technologies**