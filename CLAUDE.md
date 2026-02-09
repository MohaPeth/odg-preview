# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ODG (Ogooué Digital Gold) is a full-stack web platform for mining resource management and traceability in Gabon. The system combines geospatial data management (WebGIS), blockchain-based traceability, and operator/partner management.

**Stack:**
- Backend: Flask 3.1.1 + PostgreSQL 15+ with PostGIS extension
- Frontend: React 19 + Vite + shadcn/ui + TailwindCSS
- Blockchain: Solidity smart contracts + web3.py (currently in simulation mode)
- Maps: Leaflet + react-leaflet
- Charts: Recharts

## Development Commands

### Backend

```bash
# Navigate to backend
cd backend

# Start development server (recommended)
python run_server.py

# Create test users (admin, operator, partner)
python create_test_users.py

# Initialize production database
python init_production_db.py

# Production deployment with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

The backend runs on `http://localhost:5000`.

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the backend on port 5000 (configured in [vite.config.js](frontend/vite.config.js)).

### Database Setup

PostgreSQL credentials (development):
- Host: localhost:5432
- Database: `odg_mining`
- User: `odg_user`
- Password: `root`

The PostGIS extension must be enabled for geospatial functionality.

## Architecture

### Backend Structure

```
backend/
├── src/
│   ├── main.py                    # Flask app factory and initialization
│   ├── models/                    # SQLAlchemy data models
│   │   ├── mining_data.py         # MiningDeposit, ExploitationArea, Infrastructure, BlockchainTransaction, Operator
│   │   ├── user.py                # User model with role-based access (admin, operator, partner)
│   │   ├── geospatial_layers.py   # GeospatialLayer, LayerUploadHistory
│   │   └── substances.py          # Substance reference data
│   ├── routes/                    # API endpoint blueprints
│   │   ├── user.py                # Authentication and user CRUD
│   │   ├── operators.py           # Operator management
│   │   ├── webgis.py              # WebGIS layers endpoints
│   │   ├── geospatial_import.py   # File upload/import (KML, KMZ, SHP, GeoJSON, TIFF, CSV, TXT)
│   │   ├── blockchain.py          # Blockchain transaction CRUD
│   │   ├── blockchain_integration.py  # Blockchain status and publishing
│   │   ├── dashboard.py           # Dashboard summary statistics
│   │   └── mining_import.py       # Import gisements GeoJSON/CSV
│   ├── services/
│   │   ├── blockchain_service.py  # Web3 integration (simulation mode by default)
│   │   └── geospatial_import.py   # Geospatial file processing logic
│   └── config/
│       └── blockchain_config.py   # Blockchain network configurations
├── _archive/                       # deposit_endpoints_archive.py (archived; gisements via webgis + mining_import)
├── contracts/
│   └── ODGTraceability.sol        # Solidity smart contract for traceability
├── config_production.py           # ProductionConfig and DevelopmentConfig classes
├── run_server.py                  # Development server launcher
├── create_test_users.py           # Creates test users (admin@odg.ga, operator@odg.ga, partner@odg.ga)
├── wsgi.py                        # WSGI entry point for production
└── .env.example                   # Environment variables template
```

**Key Backend Patterns:**

1. **App Factory Pattern**: The Flask app is created via `create_app()` in [src/main.py](backend/src/main.py). Database initialization with sample data happens in `init_database()`.

2. **Blueprint-based Routing**: Each route module registers a Blueprint with a specific URL prefix (e.g., `/api`, `/api/webgis`, `/api/blockchain`).

3. **Configuration Management**: [config_production.py](backend/config_production.py) provides `ProductionConfig` and `DevelopmentConfig` classes. Environment is controlled by `FLASK_ENV` variable.

4. **Database Models**: All models inherit from SQLAlchemy's `db.Model`. Most models provide a `to_dict()` method for JSON serialization.

5. **Geospatial Data**: PostGIS is used for spatial queries. The `GeospatialLayer` model uses GeoAlchemy2 for geometry columns. File imports support KML, KMZ, Shapefile, GeoJSON, TIFF, CSV, and TXT formats.

6. **Blockchain Integration**: The blockchain service is abstracted in [src/services/blockchain_service.py](backend/src/services/blockchain_service.py). By default, `BLOCKCHAIN_ENABLED=false` in `.env`, so transactions are simulated. When enabled, it uses web3.py to interact with the deployed smart contract.

### Frontend Structure

```
frontend/
├── src/
│   ├── App.jsx                    # Root component with authentication logic
│   ├── main.jsx                   # React entry point
│   ├── components/
│   │   ├── MainApp.jsx            # Main dashboard with tab navigation (admin/operator view)
│   │   ├── PartnerDashboard.jsx   # Read-only dashboard for partners
│   │   ├── Login.jsx              # Login form (email-based authentication)
│   │   ├── WebGISMap.jsx          # Leaflet map with deposits, areas, infrastructure
│   │   ├── BlockchainDashboard.jsx  # Blockchain transactions and statistics
│   │   ├── LayersWorkspace.jsx    # Geospatial layers management
│   │   ├── UserManagement.jsx     # User CRUD
│   │   ├── PartnersManagement.jsx # Partner management
│   │   └── ui/                    # shadcn/ui components
│   └── services/
│       ├── api.js                 # Generic API utilities
│       ├── usersApi.js            # User API calls
│       ├── operatorsApi.js        # Operator API calls
│       ├── geospatialApi.js       # Geospatial/WebGIS API calls
│       └── blockchainApi.js       # Blockchain API calls
└── vite.config.js                 # Vite config with proxy to backend
```

**Key Frontend Patterns:**

1. **Role-based Rendering**: [App.jsx](frontend/src/App.jsx) checks `userProfile.role` and renders either `MainApp` (admin/operator) or `PartnerDashboard` (partner).

2. **State Management**: Uses React hooks (`useState`, `useEffect`) for local state. User profile is stored in localStorage under the key `odg_user`.

3. **Tab Navigation**: [MainApp.jsx](frontend/src/components/MainApp.jsx) uses shadcn/ui `Tabs` for navigation between Home, WebGIS, Blockchain, Layers, Users, Partners, and Settings.

4. **API Services**: Each `services/*.js` file exports functions that call the backend API. The Vite proxy forwards `/api` requests to `http://localhost:5000`.

5. **UI Components**: Uses shadcn/ui (Radix UI + TailwindCSS) for consistent design. Components are in `components/ui/`.

6. **Map Integration**: WebGIS uses Leaflet with custom markers and popups. Layers are dynamically rendered based on API data.

### Data Flow

1. **Authentication**: Login form sends email to `/api/auth/login`. Backend returns user object. Frontend stores profile in localStorage and renders appropriate dashboard.

2. **Dashboard Data**: The home tab calls `/api/dashboard/summary` to get statistics (active deposits, confirmed transactions, tracked volumes, active layers, operators count).

3. **WebGIS**: Map loads layers from `/api/webgis/layers` and renders deposits, exploitation areas, and infrastructure. File uploads go to `/api/geospatial/upload`.

4. **Blockchain**: Blockchain dashboard fetches transactions from `/api/blockchain/transactions`. Publishing to blockchain happens via `/api/blockchain-integration/publish/:id`.

5. **User/Operator Management**: CRUD operations use `/api/users` and `/api/operators` endpoints.

## Critical Security (implemented)

**Authentication is in place for production-ready deployment.**

- **Login** (`POST /api/auth/login`): requires email + password; password verified via `password_hash` (Werkzeug); JWT issued on success.
- **User model**: `password_hash` column and `set_password` / `check_password` in [backend/src/models/user.py](backend/src/models/user.py).
- **Protected routes**: All `/api/*` routes require a valid JWT except login and `GET /api/health`; see [backend/src/auth.py](backend/src/auth.py) and [backend/src/main.py](backend/src/main.py).
- **Rate limiting**: Flask-Limiter on login (e.g. 10/min per IP).
- **Before first deploy**: Run migration `add_password_hash_to_users.sql`, then `python create_test_users.py` to set test user passwords. See [docs/operations/auth-et-securite.md](docs/operations/auth-et-securite.md).

## Configuration

### Environment Variables

Copy [backend/.env.example](backend/.env.example) to `backend/.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Flask secret key for sessions (change in production!)
- `BLOCKCHAIN_ENABLED`: `true` or `false` (default: `false`)
- `BLOCKCHAIN_NETWORK`: Network name (e.g., `polygon_mumbai`)
- `BLOCKCHAIN_RPC_URL`: Optional RPC endpoint override
- `BLOCKCHAIN_PRIVATE_KEY`: Wallet private key for signing transactions
- `BLOCKCHAIN_CONTRACT_ADDRESS`: Deployed smart contract address
- `CORS_ORIGINS`: Comma-separated list of allowed origins for production

### Test Users

After running `create_test_users.py`, you can log in with:

- **Admin**: `admin@odg.ga` (full access)
- **Operator**: `operator@odg.ga` (manage deposits, transactions)
- **Partner**: `partner@odg.ga` (read-only access)

Note: Passwords are NOT currently checked by the system.

## Blockchain Smart Contract

The [ODGTraceability.sol](backend/contracts/ODGTraceability.sol) smart contract provides immutable traceability records for mining materials. Each record includes:
- Transaction hash
- Material type (Or, Diamant, etc.)
- Quantity (in grams)
- Timestamp
- Origin and destination
- Recorder address

The contract is NOT deployed by default. Blockchain features run in simulation mode unless `BLOCKCHAIN_ENABLED=true` is set and a contract is deployed.

## Common Patterns

### Adding a New API Endpoint

1. Create or modify a Blueprint in `backend/src/routes/`
2. Register the Blueprint in [backend/src/main.py](backend/src/main.py) with `app.register_blueprint()`
3. Add corresponding API functions in `frontend/src/services/`
4. Use the API functions in React components

### Adding a New Model

1. Define the model class in `backend/src/models/` inheriting from `db.Model`
2. Add a `to_dict()` method for JSON serialization
3. Import the model in [backend/src/main.py](backend/src/main.py) so SQLAlchemy registers it
4. Run the app to trigger `db.create_all()` or create a migration script

### Geospatial File Import

The system supports importing various geospatial formats:
- Vector: KML, KMZ, Shapefile (.zip), GeoJSON
- Raster: GeoTIFF
- Tabular: CSV, TXT (with lat/lon columns)

Files are processed in [backend/src/services/geospatial_import.py](backend/src/services/geospatial_import.py) using libraries like Fiona, Rasterio, and Shapely. Data is stored in the `geospatial_layers` table with PostGIS geometry columns.

## Known Limitations

1. **Blockchain in simulation mode**: No real blockchain transactions by default (`BLOCKCHAIN_ENABLED=false`).
2. **No automated tests**: Test suite needs to be created in a `tests/` directory; `deploy_production.sh` skips tests if absent.
3. **Dashboard uses mock data in some places**: Some statistics are hardcoded in components instead of fetched from API.
4. **No pagination**: Large datasets are not paginated (could cause performance issues).
5. **CORS is fully open in development**: `CORS_ORIGINS=['*']` allows all origins; production must set explicit origins.

**Security (implemented):** Login requires email + password; JWT is issued and required for all API routes except login and health; rate limiting on login; see [docs/operations/auth-et-securite.md](docs/operations/auth-et-securite.md).

## File Naming Conventions

- Backend: `snake_case` for Python files and modules
- Frontend: `PascalCase` for React components, `camelCase` for utilities
- Database: `snake_case` for table and column names
- API routes: `/api/resource-name` with hyphens

## Documentation

Project documentation is organized by responsibility (architecture, guides, métier, operations, historique):

- **[docs/README.md](docs/README.md)** – Main documentation index
- **docs/architecture/** – Technical analysis, blockchain overview, modules
- **docs/guides/** – Installation, quick start, usage, tests, geospatial import/export
- **docs/metier/** – Feature plans, geospatial implementation plan
- **docs/operations/** – PostGIS setup, production readiness, integration tests
- **docs/historique/** – Corrections, bug reports, verification (reference)

Structure follows separation of concerns and maintainability (see `.cursor rules/semantic-coding-guardrails.md`).

## Important Notes

- The `_archive/` directory in backend contains old PostgreSQL setup scripts for reference only
- Database initialization happens automatically on first run via `init_database()` in [backend/src/main.py](backend/src/main.py)
- Frontend uses path alias `@` which resolves to `frontend/src/`
- All API endpoints should use `@cross_origin()` decorator for CORS support
- PostGIS extension must be enabled manually in PostgreSQL before running the backend
