from app import celery, db, socketio
from app.models import Wallet
from app.solana_api import get_wallet_balance
from app.routes import emit_wallet_update

@celery.task
def update_wallet_balances():
    wallets = Wallet.query.all()
    for wallet in wallets:
        balance = get_wallet_balance(wallet.address)
        if wallet.balance != balance:
            wallet.balance = balance
            db.session.commit()
            emit_wallet_update(wallet)
