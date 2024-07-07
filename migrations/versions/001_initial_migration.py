"""Initial migration

Revision ID: 001_initial_migration
Revises: 
Create Date: 2024-07-06 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'users' not in tables:
        # Create users table
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=64), nullable=True),
            sa.Column('email', sa.String(length=120), nullable=True),
            sa.Column('password_hash', sa.String(length=128), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    if 'wallets' not in tables:
        # Create wallets table
        op.create_table('wallets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('address', sa.String(length=44), nullable=True),
            sa.Column('balance', sa.Float(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_wallets_address'), 'wallets', ['address'], unique=True)

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_wallets_address'), table_name='wallets')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
