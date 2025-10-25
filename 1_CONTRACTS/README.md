
# VALORA Algorand Smart Contracts (MVP)

## Structure
- contracts/stateful: Stateful contract (store product price mapping)
- contracts/stateless: Stateless contract (escrow / validation)
- scripts: Deploy & update scripts

## Setup
1. Install dependencies:
    pip install -r requirements.txt

2. Set environment variables in .env:
    ALGOD_ADDRESS=...
    ALGOD_TOKEN=...
    CREATOR_MNEMONIC=...

3. Deploy stateful contract:
    python scripts/deploy_stateful.py

4. Deploy stateless contract:
    python scripts/deploy_stateless.py

5. Update price:
    python scripts/update_price.py
