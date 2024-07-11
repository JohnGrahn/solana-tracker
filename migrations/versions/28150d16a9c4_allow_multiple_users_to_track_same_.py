# migrations/versions/28150d16a9c4_allow_multiple_users_to_track_same_.py
"""Allow multiple users to track same wallet

Revision ID: 28150d16a9c4
Revises: 30db41984098
Create Date: 2024-07-06 21:32:29.778859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28150d16a9c4'
down_revision = '30db41984098'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table for user-wallet associations
    op.create_table('user_wallets',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('wallet_id', sa.Integer(), sa.ForeignKey('wallets.id'), primary_key=True)
    )

def downgrade():
    # Drop the user_wallets table
    op.drop_table('user_wallets')