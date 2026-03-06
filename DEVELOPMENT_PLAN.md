# DEVELOPMENT PLAN: DISTROVIZ v3

## 1. ARCHITECTURE OVERVIEW

DISTROVIZ v3 is a monolithic local application with three main layers:

**Frontend (React + Vite):**
- Dashboard with KPIs and charts using Recharts
- Orders management interface with form creation
- Responsive design with Tailwind CSS (4 cols KPI + 2 cols charts >1024px, 2x2 KPIs + stacked charts 768-1024px, single column <768px)
- Lucide React icons throughout the UI

**Backend (FastAPI):**
- 5 REST endpoints: GET /api/plants, GET /api/centers, GET /api/orders, GET /api/dashboard/summary, POST /api/orders
- SQLAlchemy 2.0 ORM with Pydantic validation
- Uvicorn ASGI server

**Database (SQLite):**
- 3 tables: plants, distribution_centers, orders
- Local file-based storage with seed data

**Folder Structure:**
```
distroviz-v3/
├── frontend/src/          → React app with components, services
├── backend/              → FastAPI service with models, routes
├── shared/               → Common types and utilities
├── docs/                 → Architecture diagrams
├── docker-compose.yml    → Multi-service orchestration
└── run.sh/run.bat        → Zero-config startup scripts
```

## 2. ACCEPTANCE CRITERIA

1. **Dashboard Functionality**: User can access localhost:3000, view 4 KPIs (total orders, fulfillment rate, avg delivery days, active plants), and see 2 interactive charts showing order trends and distribution by status
2. **Orders Management**: User can view all orders in a table, create new orders via form with plant/center selection, and see real-time updates without page refresh
3. **API Completeness**: All 5 endpoints return correct JSON data, POST /api/orders validates input and creates records, GET /api/dashboard/summary calculates KPIs from actual database data
4. **Zero-Setup Deployment**: Running `./run.sh` starts all services, waits for health checks, and prints "App ready at http://localhost:3000" with no manual configuration required

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — shared types, interfaces, DB schemas, config
**Goal:** Create ALL shared code that other items will import: Pydantic models for plants/centers/orders, SQLAlchemy table definitions, environment validation, database connection utilities, and TypeScript interfaces
**Files to create:**
- shared/models.py (create) - Pydantic schemas for API requests/responses, SQLAlchemy table models for plants/distribution_centers/orders
- shared/config.py (create) - environment variable validation, database URL configuration, CORS settings
- shared/database.py (create) - SQLAlchemy engine setup, session management, connection utilities
- backend/db/schema.sql (create) - complete SQLite schema with tables, indexes, and seed data INSERT statements
- frontend/src/types/index.ts (create) - TypeScript interfaces matching Pydantic models for Plant, DistributionCenter, Order, DashboardSummary
**Never do in this item:**
- Implement business logic or route handlers
- Create UI components or API endpoints
- Add authentication or authorization logic
**Dependencies:** None
**Validation:** `python -c "from shared.models import Plant, Order; from shared.config import get_settings; print('Models imported successfully')"` executes without errors

### ITEM 2: Backend API Service — FastAPI routes with SQLAlchemy operations
**Goal:** Implement all 5 REST endpoints with complete CRUD operations, input validation, error handling, and health check endpoint
**Files to create:**
- backend/main.py (create) - FastAPI app initialization, CORS middleware, route registration, startup/shutdown events
- backend/routes/plants.py (create) - GET /api/plants endpoint returning all plants with id, name, location, capacity
- backend/routes/centers.py (create) - GET /api/centers endpoint returning all distribution centers with id, name, region, storage_capacity
- backend/routes/orders.py (create) - GET /api/orders and POST /api/orders endpoints with full CRUD, status validation, date handling
- backend/routes/dashboard.py (create) - GET /api/dashboard/summary calculating total_orders, fulfillment_rate, avg_delivery_days, active_plants from database
- backend/routes/health.py (create) - GET /health endpoint returning service status, version, database connectivity
- backend/Dockerfile (create) - multi-stage Python build with non-root user, SQLite database initialization
**Dependencies:** Item 1
**Validation:** `curl http://localhost:8000/health` returns 200 status with JSON containing service info, all 5 API endpoints respond with valid JSON data

### ITEM 3: Frontend React Application — dashboard, orders management, responsive UI
**Goal:** Build complete React SPA with dashboard KPIs/charts, orders table/form, responsive layout, and API integration service layer
**Files to create:**
- frontend/src/App.tsx (create) - main app component with routing, layout structure, error boundaries
- frontend/src/components/Dashboard.tsx (create) - dashboard page with 4 KPI cards and 2 Recharts visualizations (line chart for trends, pie chart for status distribution)
- frontend/src/components/Orders.tsx (create) - orders management page with data table and create order form modal
- frontend/src/components/Layout.tsx (create) - responsive layout component with navigation, mobile menu, Tailwind breakpoints
- frontend/src/components/KPICard.tsx (create) - reusable KPI display component with Lucide icons, loading states
- frontend/src/services/api.ts (create) - API service layer with fetch wrappers for all 5 endpoints, error handling, TypeScript return types
- frontend/src/hooks/useOrders.ts (create) - React hook for orders data fetching, caching, optimistic updates
- frontend/src/hooks/useDashboard.ts (create) - React hook for dashboard data with auto-refresh, loading states
- frontend/package.json (create) - Vite 5, React, Recharts, Tailwind CSS, Lucide React dependencies
- frontend/vite.config.ts (create) - Vite configuration with proxy to backend API, build optimization
- frontend/tailwind.config.js (create) - Tailwind configuration with responsive breakpoints, custom colors
- frontend/index.html (create) - HTML entry point with meta tags, title
- frontend/Dockerfile (create) - multi-stage Node.js build serving static files via nginx
**Dependencies:** Item 1
**Validation:** Navigate to http://localhost:3000, verify dashboard loads with KPIs and charts, create new order via form, confirm data persists and UI updates

### ITEM 4: Database Initialization & Seed Data Management
**Goal:** Create SQLite database initialization with complete seed data for plants, distribution centers, and 30 historical orders for testing and demo purposes
**Files to create:**
- backend/db/init_db.py (create) - database initialization script creating tables, indexes, and inserting seed data
- backend/db/seed_data.py (create) - comprehensive seed data with 5 plants, 8 distribution centers, 30 orders with realistic dates, statuses, quantities
- backend/db/migrations/001_initial_schema.sql (create) - SQL migration file with CREATE TABLE statements, foreign key constraints, indexes on plant_id, center_id, order_date
**Dependencies:** Item 1
**Validation:** `python backend/db/init_db.py` creates distroviz.db file, `sqlite3 distroviz.db "SELECT COUNT(*) FROM orders"` returns 30 records

### ITEM 5: Infrastructure & Deployment (REQUIRED — PROJECT MUST RUN)
**Goal:** Complete Docker setup — zero manual steps, runs with './run.sh'
**Files to create/modify:**
- docker-compose.yml (create) - backend and frontend services with healthchecks, depends_on conditions, environment variables, volume mounts for SQLite
- .env.example (create) - DATABASE_URL, BACKEND_PORT=8000, FRONTEND_PORT=3000, CORS_ORIGINS with descriptions
- .gitignore (create) - exclude node_modules, dist, .env, __pycache__, *.pyc, *.db, .vite
- .dockerignore (create) - exclude node_modules, .git, *.log, dist, .env, __pycache__
- run.sh (create) - validates Docker installation, builds images, starts services, waits for healthy status, prints access URLs
- run.bat (create) - Windows equivalent of run.sh with Docker validation and service startup
- README.md (create) - Prerequisites (Docker), Clone instructions, Run command (./run.sh), Testing endpoints, Architecture overview
- docs/architecture.md (create) - system architecture diagram, component descriptions, API documentation, database schema
**Dependencies:** Items 1, 2, 3, 4
**Validation:** './run.sh' completes without errors, all services report healthy status, web app accessible at localhost:3000, all API endpoints respond correctly with sample data, dashboard displays KPIs and charts with seed data
**CRITICAL:** Zero manual steps — clone → ./run.sh → working app with populated dashboard and functional order creation