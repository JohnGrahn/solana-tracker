from app import celery, db, socketio
from app.models import Wallet, User
from app.solana_api import get_wallet_balance, get_transaction_history, get_wallet_token_balances
from app.helius_api import get_wallet_info
from flask import current_app
from sqlalchemy.orm import sessionmaker

@celery.task
def update_wallet_data():
    with current_app.app_context():
        Session = sessionmaker(bind=db.engine)
        
        wallet_ids = db.session.query(Wallet.id).all()
        
        for (wallet_id,) in wallet_ids:
            session = Session()
            try:
                wallet = session.query(Wallet).get(wallet_id)
                if wallet:
                    balance = get_wallet_balance(wallet.address)
                    transactions = get_transaction_history(wallet.address)
                    token_balances = get_wallet_token_balances(wallet.address)
                    wallet_info = get_wallet_info(wallet.address)
                    
                    wallet.balance = balance
                    wallet.transactions = transactions
                    wallet.token_balances = token_balances
                    wallet.additional_info = wallet_info
                    
                    session.commit()
                    emit_wallet_update(wallet)
            except Exception as e:
                print(f"Error updating data for wallet {wallet.address}: {str(e)}")
            finally:
                session.close()

@celery.task
def update_wallet_balances():
    update_wallet_data.delay()

@celery.task
def add_wallet(user_id, address):
    with current_app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            user = session.query(User).get(user_id)
            if user:
                wallet = Wallet(address=address)
                user.wallets.append(wallet)
                session.add(wallet)
                session.commit()
                
                balance = get_wallet_balance(address)
                transactions = get_transaction_history(address)
                token_balances = get_wallet_token_balances(address)
                wallet_info = get_wallet_info(address)
                
                wallet.balance = balance
                wallet.transactions = transactions
                wallet.token_balances = token_balances
                wallet.additional_info = wallet_info
                
                session.commit()
                emit_wallet_update(wallet)
                return wallet.id
            else:
                print(f"User with id {user_id} not found")
                return None
        finally:
            session.close()

def emit_wallet_update(wallet):
    socketio.emit('wallet_update', {
        'wallet_id': wallet.id,
        'address': wallet.address,
        'balance': wallet.balance,
        'transactions': wallet.transactions,
        'token_balances': wallet.token_balances,
        'additional_info': wallet.additional_info
    }, room=f'wallet_{wallet.id}')
