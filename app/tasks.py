from app import celery, db, socketio
from app.models import Wallet, User
from app.solana_api import get_wallet_balance
from flask import current_app

@celery.task
def update_wallet_balances():
    with current_app.app_context():
        wallets = Wallet.query.all()
        updated_wallets = []

        for wallet in wallets:
            try:
                balance = get_wallet_balance(wallet.address)
                if wallet.balance != balance:
                    wallet.balance = balance
                    updated_wallets.append(wallet)
            except Exception as e:
                print(f"Error updating balance for wallet {wallet.address}: {str(e)}")

        if updated_wallets:
            db.session.commit()
            for wallet in updated_wallets:
                emit_wallet_update(wallet)

@celery.task
def add_wallet(user_id, address):
    with current_app.app_context():
        user = User.query.get(user_id)
        if user:
            wallet = Wallet(address=address)
            user.wallets.append(wallet)
            db.session.add(wallet)
            db.session.commit()
            balance = get_wallet_balance(address)
            wallet.balance = balance
            db.session.commit()
            emit_wallet_update(wallet)
        else:
            print(f"User with id {user_id} not found")

def emit_wallet_update(wallet):
    socketio.emit('wallet_update', {
        'wallet_id': wallet.id,
        'address': wallet.address,
        'balance': wallet.balance
    }, room=f'wallet_{wallet.id}')
