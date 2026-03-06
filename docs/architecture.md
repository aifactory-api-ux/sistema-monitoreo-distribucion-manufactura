# DistroViz v3 - System Architecture

This document provides a comprehensive overview of the DistroViz v3 system architecture, component interactions, and technical implementation details.

## 🏗️ System Overview

DistroViz v3 is a containerized web application designed for distribution management and analytics. The system follows a three-tier architecture pattern with clear separation of concerns.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
│   Port: 3000    │    │   Port: 8000    │    │   File-based    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Architecture Principles

- **Containerization First**: Every component runs in Docker containers
- **API-Driven**: RESTful API with OpenAPI documentation
- **Responsive Design**: Mobile-first UI with progressive enhancement
- **Zero Configuration**: Single command deployment
- **Health Monitoring**: Built-in health checks and monitoring

## 📦 Component Architecture

### Frontend Layer (React + TypeScript)

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling and dev server
- Tailwind CSS for styling
- Recharts for data visualization
- Lucide React for icons

**Component Structure:**
```
frontend/src/
├── components/
│   ├── Dashboard.tsx      # Main dashboard with KPIs and charts
│   ├── Orders.tsx         # Orders management interface
│   ├── Layout.tsx         # Application shell and navigation
│   ├── KPICard.tsx        # Reusable KPI display component
│   ├── LoadingSpinner.tsx # Loading state component
│   └── ErrorBoundary.tsx  # Error handling wrapper
├── hooks/
│   ├── useDashboard.ts    # Dashboard data fetching logic
│   └── useOrders.ts       # Orders CRUD operations
├── services/
│   └── api.ts             # HTTP client and API methods
└── types/
    └── index.ts           # TypeScript type definitions
```

**Key Features:**
- **Responsive Layout**: 4-column KPIs + 2-column charts (>1024px), 2x2 KPIs + stacked charts (768-1024px), single column (<768px)
- **Real-time Updates**: Automatic data refresh without page reload
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Loading States**: Skeleton screens and spinners for better UX

### Backend Layer (FastAPI + SQLAlchemy)

**Technology Stack:**
- FastAPI for REST API framework
- SQLAlchemy 2.0 for ORM and database operations
- Pydantic for data validation and serialization
- Uvicorn as ASGI server

**API Structure:**
```
backend/
├── routes/
│   ├── dashboard.py       # KPI calculations and summary data
│   ├── orders.py          # Orders CRUD operations
│   ├── plants.py          # Plants data endpoints
│   ├── centers.py         # Distribution centers endpoints
│   └── health.py          # Health check endpoint
├── db/
│   ├── schema.sql         # Database schema definition
│   ├── seed_data.py       # Sample data generation
│   └── init_db.py         # Database initialization
└── main.py                # FastAPI application setup
```

**API Endpoints:**

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/api/health` | Service health status | `{"status": "healthy"}` |
| GET | `/api/dashboard/summary` | KPIs and metrics | Dashboard summary object |
| GET | `/api/orders` | List orders with filtering | Array of order objects |
| POST | `/api/orders` | Create new order | Created order object |
| GET | `/api/plants` | Available plants | Array of plant objects |
| GET | `/api/centers` | Distribution centers | Array of center objects |

### Database Layer (SQLite)

**Schema Design:**

```sql
-- Plants table
CREATE TABLE plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

-- Distribution Centers table
CREATE TABLE distribution_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    distribution_center_id INTEGER NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'medium',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plant_id) REFERENCES plants (id),
    FOREIGN KEY (distribution_center_id) REFERENCES distribution_centers (id)
);
```

**Indexes for Performance:**
```sql
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_plant_id ON orders(plant_id);
CREATE INDEX idx_orders_center_id ON orders(distribution_center_id);
CREATE INDEX idx_orders_date ON orders(order_date);
```

## 🐳 Container Architecture

### Docker Compose Configuration

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
```

### Multi-Stage Docker Builds

**Backend Dockerfile:**
```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
# Builder stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

## 🔄 Data Flow Architecture

### Request Flow

1. **User Interaction**: User interacts with React components
2. **API Call**: Frontend makes HTTP request via api service
3. **Route Handling**: FastAPI routes receive and validate request
4. **Database Query**: SQLAlchemy executes database operations
5. **Response**: Data flows back through the same path
6. **UI Update**: React components re-render with new data

### State Management

```typescript
// Custom hooks manage component state
const useDashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch data with error handling
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await api.getDashboardSummary();
      setData(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return { data, loading, error, refetch: fetchData };
};
```

## 📊 Performance Architecture

### Frontend Optimizations
- **Code Splitting**: Vendor, charts, icons, and router bundles
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Debounced Requests**: Prevent excessive API calls

### Backend Optimizations
- **Async Operations**: FastAPI async/await pattern
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Indexed database queries
- **Response Caching**: HTTP cache headers

### Database Optimizations
- **Indexes**: Strategic indexing on frequently queried columns
- **Query Planning**: Optimized SQL queries
- **Connection Reuse**: Persistent database connections

## 🔒 Security Architecture

### Application Security
- **Input Validation**: Pydantic models validate all inputs
- **CORS Protection**: Configured allowed origins
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **XSS Protection**: React's built-in XSS prevention

### Container Security
- **Non-root Users**: All containers run as non-root
- **Minimal Images**: Alpine/slim base images
- **No Secrets in Images**: Environment variables only
- **Health Checks**: Monitor container health

## 🚀 Deployment Architecture

### Zero-Config Deployment

```bash
# Single command deployment
./run.sh
```

**Deployment Steps:**
1. Validate Docker installation
2. Create necessary directories
3. Setup environment variables
4. Build container images
5. Start services with health checks
6. Wait for all services to be healthy
7. Test API endpoints
8. Display access information

### Health Monitoring

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## 📈 Monitoring & Observability

### Application Metrics
- **Health Endpoints**: Service availability monitoring
- **Response Times**: API performance tracking
- **Error Rates**: Application error monitoring
- **Resource Usage**: Container resource consumption

### Logging Strategy
- **Structured Logging**: JSON formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Tracing**: Unique request IDs
- **Error Context**: Stack traces and context data

## 🔧 Development Architecture

### Development Workflow
1. **Local Development**: Docker Compose for consistent environment
2. **Hot Reloading**: Vite dev server and FastAPI auto-reload
3. **Type Safety**: TypeScript throughout the stack
4. **Code Quality**: ESLint, Prettier, and Python formatting

### Testing Strategy
- **Unit Tests**: Component and function testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full user workflow testing
- **Health Checks**: Automated service validation

## 🎯 Scalability Considerations

### Horizontal Scaling
- **Stateless Services**: No server-side session state
- **Database Scaling**: Read replicas and connection pooling
- **Load Balancing**: Multiple container instances
- **Caching Layer**: Redis for session and data caching

### Vertical Scaling
- **Resource Limits**: Container CPU and memory limits
- **Connection Pooling**: Database connection optimization
- **Query Optimization**: Efficient database queries
- **Asset Optimization**: Compressed and minified assets

## 📋 Configuration Management

### Environment Variables
```env
# Database Configuration
DATABASE_URL=sqlite:///./data/distroviz.db

# Service Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000

# CORS Settings
CORS_ORIGINS=http://localhost:3000

# Application Settings
NODE_ENV=production
VITE_API_URL=http://localhost:8000
```

### Configuration Validation
- **Required Variables**: Application fails fast if missing
- **Type Validation**: Environment variable type checking
- **Default Values**: Sensible defaults for optional settings
- **Documentation**: Clear descriptions in .env.example

---

**This architecture provides a solid foundation for a scalable, maintainable, and secure distribution management application.**