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
from app.tasks import update_wallet_balances, add_wallet  # Added this import
from app.helius_api import get_detailed_transactions, get_token_balances, get_wallet_info


bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    update_wallet_balances.delay()
    fresh_user = db.session.query(User).options(db.joinedload(User.wallets)).get(current_user.id)
    return render_template('dashboard.html', wallets=fresh_user.wallets)


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
def add_wallet_route():
    address = request.form['address']
    wallet_id = add_wallet.delay(current_user.id, address).get()
    if wallet_id:
        flash('Wallet has been added and balance fetched.')
    else:
        flash('Error adding wallet. Please try again.')
    return redirect(url_for('main.index'))


@bp.route('/wallet/<int:wallet_id>')
@login_required
def wallet_detail(wallet_id):
    wallet = Wallet.query.get_or_404(wallet_id)
    if wallet not in current_user.wallets:
        flash('Access denied')
        return redirect(url_for('main.index'))
    try:
        balance = wallet.balance
        detailed_transactions = get_detailed_transactions(wallet.address)
        token_balances = get_token_balances(wallet.address)
        wallet_info = get_wallet_info(wallet.address)
    except Exception as e:
        flash(f'Error fetching wallet details: {str(e)}')
        balance = None
        detailed_transactions = []
        token_balances = []
        wallet_info = {}
    return render_template('wallet_detail.html', wallet=wallet, balance=balance, 
                           transactions=detailed_transactions, token_balances=token_balances, 
                           wallet_info=wallet_info)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        for wallet in current_user.wallets:
            join_room(f'wallet_{wallet.id}')

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        for wallet in current_user.wallets:
            leave_room(f'wallet_{wallet.id}')
