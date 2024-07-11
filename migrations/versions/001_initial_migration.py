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
    pass  # Remove table creation code here - it's now in migration 30db41984098... 

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_wallets_address'), table_name='wallets')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')