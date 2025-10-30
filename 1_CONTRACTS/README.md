
# VALORA Algorand Smart Contracts (MVP)

This folder contains a minimal stateful application that supports TWO transactions per price update:
- First transaction: record the LOWEST market price for a product_id
- Second transaction: record the DISPLAY price (lowest minus margin 3–5%) for the same product_id

The backend currently supports both modes:
- Simple note-storage (APP_ID = 1): two payment txs to self with JSON notes (lowest, then display)
- Smart-contract (APP_ID > 1): two application call txs to methods update_lowest and update_display

## Structure
- contracts/stateful/price_app.py: PyTeal app storing lowest_paise and display_paise in boxes keyed by product_id
- scripts/deploy_stateful.py: compile + deploy the app; prints APP_ID
- scripts/update_prices.py: demonstrates sending an atomic group with two app-calls (lowest then display)

## Setup
1. Install dependencies:
    pip install -r requirements.txt

2. Set environment variables in .env:
    ALGOD_ADDRESS=...
    ALGOD_TOKEN=...
    CREATOR_MNEMONIC=...    # Wallet mnemonic (oracle)

3. Deploy stateful contract:
    python scripts/deploy_stateful.py
    # save the APP_ID printed and put it in 3_BACKEND/.env (APP_ID=>1 to enable smart-contract mode)

4. Update prices (two txs atomically):
    python scripts/update_prices.py --app-id APP_ID --product-id 1 --lowest 199990 --display 193990

## Flow & Effect

1) First transaction (LOWEST)
- Either: Payment note with JSON or App call: update_lowest(product_id, lowest_paise)
- Effect: Chain has an immutable record of the computed lowest price for that run

2) Second transaction (DISPLAY)
- Either: Payment note JSON or App call: update_display(product_id, display_paise)
- Effect: Chain stores the derived selling price after applying margin; backend also persists to DB and broadcasts WS

The frontend subscribes to ws://.../ws/prices/{product_id} and shows DISPLAY price live; the products list endpoints
now also return the latest display_paise/display_price_readable for consistency.
