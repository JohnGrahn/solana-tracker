import requests
from config import Config
from app.helius_api import get_detailed_transactions, get_token_balances

def get_wallet_balance(address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    response = requests.post(Config.SOLANA_RPC_URL, json=payload)
    if response.status_code == 200:
        result = response.json().get('result', {})
        return result.get('value', 0) / 1e9  # Convert lamports to SOL
    return 0

def get_transaction_history(address, limit=10):
    return get_detailed_transactions(address, limit)

def get_wallet_token_balances(address):
    return get_token_balances(address)
