"""Allow multiple users to track same wallet

Revision ID: 28150d16a9c4
Revises: 30db41984098
Create Date: 2024-07-06 21:32:29.778859

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '28150d16a9c4'
down_revision = '30db41984098'
branch_labels = None
depends_on = None


def upgrade():
    # Remove unique constraint from wallets address
    op.drop_index('ix_wallets_address', table_name='wallets')
    op.create_index(op.f('ix_wallets_address'), 'wallets', ['address'], unique=False)
    
    # Remove the unique constraint on address and user_id
    op.drop_constraint('uix_address_user', 'wallets', type_='unique')
    
    # Create a new table for user-wallet associations
    op.create_table('user_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate existing wallet-user relationships to the new table
    op.execute(
        "INSERT INTO user_wallets (user_id, wallet_id) "
        "SELECT user_id, id FROM wallets WHERE user_id IS NOT NULL"
    )
    
    # Remove the user_id column from wallets table
    op.drop_constraint('wallets_user_id_fkey', 'wallets', type_='foreignkey')
    op.drop_column('wallets', 'user_id')


def downgrade():
    # Add back user_id to wallets
    op.add_column('wallets', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('wallets_user_id_fkey', 'wallets', 'users', ['user_id'], ['id'])
    
    # Migrate data back from user_wallets to wallets
    op.execute(
        "UPDATE wallets SET user_id = user_wallets.user_id "
        "FROM user_wallets WHERE wallets.id = user_wallets.wallet_id"
    )
    
    # Drop the user_wallets table
    op.drop_table('user_wallets')
    
    # Restore unique constraint on wallets address
    op.drop_index(op.f('ix_wallets_address'), table_name='wallets')
    op.create_index('ix_wallets_address', 'wallets', ['address'], unique=True)
    
    # Restore the unique constraint on address and user_id
    op.create_unique_constraint('uix_address_user', 'wallets', ['address', 'user_id'])
