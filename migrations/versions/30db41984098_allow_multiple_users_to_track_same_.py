"""Allow multiple users to track same wallet

Revision ID: 30db41984098
Revises: 001_initial_migration
Create Date: 2024-07-06 19:37:22.904986

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '30db41984098'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), index=True, unique=True),
        sa.Column('email', sa.String(length=120), index=True, unique=True),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create wallets table
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=44), index=True),
        sa.Column('balance', sa.Float(), default=0.0),
        sa.PrimaryKeyConstraint('id')
    )


# No downgrade function needed in this case
# def downgrade():
#     pass 