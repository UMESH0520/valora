from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ENV = os.path.join(BASE, ".env")
load_dotenv(ENV)

ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
ORACLE_MNEMONIC = os.getenv("CREATOR_MNEMONIC") or os.getenv("ORACLE_MNEMONIC")


def get_client() -> algod.AlgodClient:
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def get_oracle():
    sk = mnemonic.to_private_key(ORACLE_MNEMONIC)
    addr = account.address_from_private_key(sk)
    return sk, addr


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-id", type=int, required=True)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--lowest", type=int, required=True, help="paise")
    parser.add_argument("--display", type=int, required=True, help="paise")
    args = parser.parse_args()

    client = get_client()
    sk, addr = get_oracle()
    sp = client.suggested_params(); sp.flat_fee=True; sp.fee=1000

    # Build two app calls in one atomic group
    app_id = args.app_id
    pid = args.product_id.encode()

    tx1 = transaction.ApplicationNoOpTxn(
        sender=addr, sp=sp, index=app_id,
        app_args=[b"update_lowest", pid, args.lowest.to_bytes(8, 'big')],
    )
    tx2 = transaction.ApplicationNoOpTxn(
        sender=addr, sp=sp, index=app_id,
        app_args=[b"update_display", pid, args.display.to_bytes(8, 'big')],
    )

    gid = transaction.calculate_group_id([tx1, tx2])
    tx1.group = gid; tx2.group = gid

    stx1 = tx1.sign(sk)
    stx2 = tx2.sign(sk)

    txid = client.send_transactions([stx1, stx2])
    print("GROUP_TX:", txid)
