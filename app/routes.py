from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Wallet
from app.solana_api import get_wallet_balance, get_transaction_history
from app import socketio

from flask_socketio import join_room
from flask_socketio import leave_room

from werkzeug.security import generate_password_hash

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
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.login'))
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
    wallet = Wallet(address=address, owner=current_user)
    db.session.add(wallet)
    db.session.commit()
    flash('Wallet added successfully')
    return redirect(url_for('main.index'))

@bp.route('/wallet/<int:wallet_id>')
@login_required
def wallet_detail(wallet_id):
    wallet = Wallet.query.get_or_404(wallet_id)
    if wallet.owner != current_user:
        flash('Access denied')
        return redirect(url_for('main.index'))
    balance = get_wallet_balance(wallet.address)
    transactions = get_transaction_history(wallet.address)
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
    socketio.emit('wallet_update', {
        'id': wallet.id,
        'address': wallet.address,
        'balance': wallet.balance
    }, room=wallet.owner.id)