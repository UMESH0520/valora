# VALORA - Final MVP (Enhanced)

This package contains a full final MVP for VALORA with:
- 1_CONTRACTS: PyTEAL smart contract + deploy scaffold
- 2_FRONTEND: Vite + React frontend (demo)
- 3_BACKEND: FastAPI backend with adapters, services, demo data, and Algorand submitter stub
- 4_TESTS: pytest unit tests for backend
- .github/workflows/ci.yml: CI pipeline for backend tests

Quickstart (Windows PowerShell):
1. Backend:
   cd 3_BACKEND
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   copy .env.example .env
   # (edit .env to add ALGOD keys if needed)
   python run.py

2. Frontend:
   cd 2_FRONTEND
   npm install
   npm run dev

3. Tests:
   cd ..
   python -m pytest 4_TESTS -q

Smart contract:
- 1_CONTRACTS/product_price_contract.py contains PyTEAL source. Use deploy_contract.py as scaffold to compile TEAL.
