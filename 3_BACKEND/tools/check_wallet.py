from __future__ import annotations

import os
from dotenv import load_dotenv
from algosdk import mnemonic, account
from algosdk.v2client import algod

# Load env from project .env
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV_PATH = os.path.join(BASE, ".env")
load_dotenv(ENV_PATH)

mn = os.environ.get("ORACLE_MNEMONIC")
assert mn, "ORACLE_MNEMONIC not set"

# Derive address
pk = mnemonic.to_private_key(mn)
addr = account.address_from_private_key(pk)
print("ADDRESS:", addr)

# Check algod status
algod_address = os.environ.get("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
algod_token = os.environ.get("ALGOD_API_TOKEN", "")
client = algod.AlgodClient(algod_token, algod_address)
status = client.status()
print("ALGOD_OK:", True, "LAST_ROUND:", status.get("last-round"))
