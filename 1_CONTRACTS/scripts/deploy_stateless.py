
from algosdk import algod
import os
ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN")
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
print("Stateless contract deployment script ready")
