from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Wallet
from app.solana_api import get_wallet_balance, get_transaction_history
from app import socketio
from flask_socketio import join_room, leave_room
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import make_transient
from sqlalchemy.orm.session import Session


bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('dashboard.html', wallets=current_user.wallets)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('main.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose different ones.')
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/add_wallet', methods=['POST'])
@login_required
def add_wallet():
    address = request.form['address']
    try:
        # Create a new session
        session = Session(db.engine)

        # Check if the wallet already exists
        wallet = session.query(Wallet).filter_by(address=address).first()
        if not wallet:
            wallet = Wallet(address=address)
            session.add(wallet)
        else:
            # Detach the wallet from any previous session
            session.expunge(wallet)
            make_transient(wallet)
            session.add(wallet)

        # Check if the current user already has this wallet
        user = session.merge(current_user)
        if wallet not in user.wallets:
            user.wallets.append(wallet)
            session.commit()
            flash('Wallet added successfully')
        else:
            flash('You are already tracking this wallet.')
    except Exception as e:
        session.rollback()
        flash(f'Error adding wallet: {str(e)}')
    finally:
        session.close()
    return redirect(url_for('main.index'))




@bp.route('/wallet/<int:wallet_id>')
@login_required
def wallet_detail(wallet_id):
    wallet = Wallet.query.get_or_404(wallet_id)
    if wallet not in current_user.wallets:
        flash('Access denied')
        return redirect(url_for('main.index'))
    try:
        balance = get_wallet_balance(wallet.address)
        transactions = get_transaction_history(wallet.address)
    except Exception as e:
        flash(f'Error fetching wallet details: {str(e)}')
        balance = None
        transactions = []
    return render_template('wallet_detail.html', wallet=wallet, balance=balance, transactions=transactions)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(current_user.id)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(current_user.id)

def emit_wallet_update(wallet):
    for user in wallet.users:
        socketio.emit('wallet_update', {
            'id': wallet.id,
            'address': wallet.address,
            'balance': wallet.balance
        }, room=user.id)
