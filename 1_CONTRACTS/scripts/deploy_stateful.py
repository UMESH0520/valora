from __future__ import annotations

import os
from typing import Tuple
from dotenv import load_dotenv
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from pyteal import compileTeal, Mode
import sys
# Ensure 'contracts' package is importable from project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, BASE_DIR)
from contracts.stateful.price_app import PriceApp

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV = os.path.join(BASE, ".env")
load_dotenv(ENV)

ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
CREATOR_MNEMONIC = os.getenv("CREATOR_MNEMONIC") or os.getenv("ORACLE_MNEMONIC")


def get_client() -> algod.AlgodClient:
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def get_acct() -> Tuple[str, str]:
    sk = mnemonic.to_private_key(CREATOR_MNEMONIC)
    addr = account.address_from_private_key(sk)
    return sk, addr


if __name__ == "__main__":
    client = get_client()
    sk, addr = get_acct()

    approval_teal = compileTeal(PriceApp().approval(), Mode.Application, version=8)
    clear_teal = compileTeal(PriceApp().clear(), Mode.Application, version=8)

    import base64
    approval = base64.b64decode(client.compile(approval_teal)["result"])
    clear = base64.b64decode(client.compile(clear_teal)["result"])

    sp = client.suggested_params(); sp.flat_fee=True; sp.fee=1000
    app_txn = transaction.ApplicationCreateTxn(
        sender=addr,
        sp=sp,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=transaction.StateSchema(0, 1),
        local_schema=transaction.StateSchema(0, 0),
        extra_pages=1,
    )
    stxn = app_txn.sign(sk)
    txid = client.send_transaction(stxn)
    p = client.pending_transaction_info(txid)
    while not p.get("confirmed-round"):
        client.status_after_block(client.status()["last-round"] + 1)
        p = client.pending_transaction_info(txid)
    app_id = p["application-index"]
    print("APP_ID:", app_id)

    # Set oracle address to the creator by default
    sp = client.suggested_params(); sp.flat_fee=True; sp.fee=1000
    init_txn = transaction.ApplicationNoOpTxn(
        sender=addr,
        sp=sp,
        index=app_id,
        app_args=[b"init", addr.encode()],
    )
    stxn2 = init_txn.sign(sk)
    txid2 = client.send_transaction(stxn2)
    print("INIT_TX:", txid2)
