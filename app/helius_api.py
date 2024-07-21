import requests
from config import Config

def get_detailed_transactions(address, limit=10):
    url = f"{Config.HELIUS_API_URL}/v0/addresses/{address}/transactions"
    params = {
        "api-key": Config.HELIUS_API_KEY,
        "limit": limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return [process_transaction(tx) for tx in response.json()]
    return []

def process_transaction(tx):
    return {
        'type': tx.get('type', 'Unknown'),
        'amount': tx.get('amount', 0) / 1e9,  # Convert lamports to SOL
        'balance_before': tx.get('balanceBefore', 0) / 1e9,
        'balance_after': tx.get('balanceAfter', 0) / 1e9,
        'timestamp': tx.get('timestamp', ''),
        'signature': tx.get('signature', '')
    }

def get_token_balances(address):
    url = f"{Config.HELIUS_API_URL}/v0/addresses/{address}/balances"
    params = {
        "api-key": Config.HELIUS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        balances = response.json()
        return [get_asset_details(token) for token in balances.get('tokens', [])]
    return []

def get_asset_details(token):
    mint_address = token['mint']
    url = f"{Config.HELIUS_API_URL}/v0/token-metadata"
    params = {
        "api-key": Config.HELIUS_API_KEY
    }
    data = {
        "mintAccounts": [mint_address]
    }
    response = requests.post(url, json=data, params=params)
    if response.status_code == 200:
        asset_data = response.json()[0]
        return {
            'name': asset_data.get('onChainMetadata', {}).get('metadata', {}).get('data', {}).get('name', 'Unknown'),
            'symbol': asset_data.get('onChainMetadata', {}).get('metadata', {}).get('data', {}).get('symbol', ''),
            'balance': token.get('amount', 0) / (10 ** token.get('decimals', 0)),
            'price': token.get('price', None),
            'value': token.get('value', None)
        }
    return None


def get_wallet_info(address):
    url = f"{Config.HELIUS_API_URL}/v0/addresses/{address}/info"
    params = {
        "api-key": Config.HELIUS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {}
