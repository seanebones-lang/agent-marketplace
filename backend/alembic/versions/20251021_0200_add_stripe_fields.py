"""Add Stripe fields to customers

Revision ID: 002_stripe_fields
Revises: 001_initial
Create Date: 2025-10-21 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_stripe_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Stripe fields to customers table
    op.add_column('customers', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('customers', sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_customers_stripe_customer_id'), 'customers', ['stripe_customer_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_customers_stripe_customer_id'), table_name='customers')
    
    # Drop columns
    op.drop_column('customers', 'stripe_subscription_id')
    op.drop_column('customers', 'stripe_customer_id')

