# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

VALORA is a multi-component price comparison and e-commerce platform with:
- Algorand blockchain integration for price oracles
- FastAPI backend with web scraping adapters
- React + Vite + shadcn/ui frontend
- PyTeal smart contracts for on-chain price verification

## Repository Structure

```
VALORA/
├── 1_CONTRACTS/     # Algorand smart contracts (PyTeal)
├── 2_FRONTEND/      # React + Vite + TypeScript + shadcn/ui
├── 3_BACKEND/       # FastAPI price aggregation service
└── 4_TESTS/         # pytest unit tests
```

## Common Commands

### Backend (3_BACKEND)
```powershell
# Setup (Windows PowerShell)
cd 3_BACKEND
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

# Run development server (with hot reload)
python run.py

# Access API docs
# http://127.0.0.1:8000/docs
```

### Frontend (2_FRONTEND)
```powershell
# Setup
cd 2_FRONTEND
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Lint
npm run lint

# Preview production build
npm run preview
```

### Smart Contracts (1_CONTRACTS)
```powershell
# Setup
cd 1_CONTRACTS
pip install -r requirements.txt

# Configure .env with Algorand credentials:
# ALGOD_ADDRESS, ALGOD_TOKEN, CREATOR_MNEMONIC

# Deploy stateful contract (price storage)
python scripts/deploy_stateful.py

# Deploy stateless contract (escrow/validation)
python scripts/deploy_stateless.py

# Update price on-chain
python scripts/update_price.py
```

### Tests (4_TESTS)
```powershell
# Run all tests from project root
python -m pytest 4_TESTS -q

# Run specific test file
python -m pytest 4_TESTS/test_fetch_prices.py -v
```

## Architecture

### Backend Service Architecture (3_BACKEND)
The backend follows a layered architecture:

1. **Adapters Layer** (`app/adapters/`)
   - Platform-specific scrapers: `amazon.py`, `flipkart.py`, `myntra.py`
   - Each adapter fetches raw product prices from e-commerce sites
   - Returns normalized data: `{adapter, product_id, price, shipping, confidence}`

2. **AI/Processing Layer** (`app/ai/`)
   - `fetcher.py`: Orchestrates parallel calls to all adapters
   - `normalizer.py`: Converts prices to paise (1/100 rupee) for precision
   - `aggregator.py`: Statistical outlier rejection (IQR method) and price aggregation
   - Final output: lowest reliable price with supporting sources

3. **Services Layer** (`app/services/`)
   - `price_service.py`: Main business logic
   - Product registry (PRODUCT_REGISTRY): In-memory catalog of tracked products
   - `compute()`: End-to-end price calculation with margin adjustment
   - Triggers blockchain submission via contracts layer

4. **Contracts Layer** (`app/contracts/`)
   - `submitter.py`: Algorand integration stub
   - Submits verified prices to blockchain (currently prepared but not fully executed)
   - Requires ALGOD_ADDRESS, ALGOD_API_TOKEN, ORACLE_MNEMONIC, APP_ID in .env

5. **Routes Layer** (`app/routes/`)
   - `health_route.py`: Health check endpoint
   - `price_routes.py`: Price computation API endpoints
   - FastAPI with CORS enabled for local frontend (ports 5173, 3000)

### Frontend Architecture (2_FRONTEND)
- **Framework**: Vite + React 18 + TypeScript
- **UI**: shadcn/ui components + Tailwind CSS + Radix UI primitives
- **Routing**: react-router-dom with routes for Index, Cart, Checkout, etc.
- **State**: CartContext provider for shopping cart state
- **Queries**: @tanstack/react-query for data fetching
- **Payment**: Razorpay integration

**Key directories**:
- `src/components/` - React components
- `src/components/ui/` - shadcn/ui components
- `src/pages/` - Route pages (Index, Cart, Checkout, etc.)
- `src/context/` - React context providers
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility functions

### Smart Contracts (1_CONTRACTS)
- **Stateful Contract** (`contracts/stateful/valora_stateful.py`): Stores product-price mappings on Algorand blockchain
- **Stateless Contract** (`contracts/stateless/valora_stateless.py`): Escrow and validation logic
- **Deployment**: Separate scripts for each contract type in `scripts/`
- **SDK**: py-algorand-sdk 2.0.2

## Important Implementation Notes

### Backend Price Flow
1. Client requests price for product_id (e.g., "VAL-PRD-001")
2. System fetches from PRODUCT_REGISTRY
3. All adapters (Amazon, Flipkart, Myntra) scrape in parallel
4. Prices normalized to paise (₹1 = 100 paise)
5. Statistical outlier rejection using IQR (interquartile range)
6. Lowest valid price selected
7. Display price calculated with margin reduction (default 3%)
8. Result includes supporting adapters and all sources
9. Async attempt to submit to Algorand blockchain

### Environment Configuration
Backend requires `.env` file with:
- `DATABASE_URL` - SQLite path (default: sqlite:///./valora.db)
- `ALGOD_ADDRESS` - Algorand node address
- `ALGOD_API_TOKEN` - Algorand API token
- `ORACLE_MNEMONIC` - Oracle account mnemonic for signing
- `APP_ID` - Deployed smart contract application ID

Contracts require similar Algorand configuration in `1_CONTRACTS/.env`.

### Testing
- Backend tests use pytest
- Run from project root to ensure correct Python path resolution
- Tests validate price fetching and contract interactions

## Development Notes

### Adding New E-commerce Adapters
1. Create new file in `3_BACKEND/app/adapters/`
2. Implement `async def fetch(session, product)` function
3. Return dict with: `adapter`, `product_id`, `price`, `shipping`, `confidence`
4. Register adapter in `fetcher.py`

### Frontend-Backend Integration
- Backend runs on `http://127.0.0.1:8000`
- Frontend expects backend at this address
- CORS configured for localhost:5173 (Vite default) and localhost:3000
- API documentation available at `/docs` (Swagger UI)

### Blockchain Integration
- Currently in stub/demo mode
- Full integration requires valid Algorand node credentials
- `submit_update()` logs intention but doesn't execute transactions by default
- Set APP_ID to deployed contract ID for live submissions
