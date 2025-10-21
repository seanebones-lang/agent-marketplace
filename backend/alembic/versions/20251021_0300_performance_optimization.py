"""Performance optimization: indexes and partitioning

Revision ID: 20251021_0300
Revises: 20251021_0200
Create Date: 2025-10-21 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251021_0300'
down_revision = '20251021_0200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes and table partitioning"""
    
    # Add composite indexes for hot queries
    op.create_index(
        'idx_deployments_customer_status',
        'deployments',
        ['customer_id', 'status'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_deployments_customer_last_used',
        'deployments',
        ['customer_id', 'last_used_at'],
        postgresql_using='btree',
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_usage_logs_customer_created',
        'usage_logs',
        ['customer_id', 'created_at'],
        postgresql_using='btree',
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_usage_logs_package_created',
        'usage_logs',
        ['package_id', 'created_at'],
        postgresql_using='btree',
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_usage_logs_status',
        'usage_logs',
        ['status'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Add index on customer email for faster lookups
    op.create_index(
        'idx_customers_email_active',
        'customers',
        ['email', 'is_active'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Add GIN index for JSONB metadata searches
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usage_logs_metadata_gin
        ON usage_logs USING gin (metadata jsonb_path_ops)
    """)
    
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_config_gin
        ON deployments USING gin (config jsonb_path_ops)
    """)
    
    # Add partial indexes for active records
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_active
        ON customers (id, org_name)
        WHERE is_active = 1
    """)
    
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deployments_active
        ON deployments (customer_id, package_id, deployed_at)
        WHERE status = 'active'
    """)
    
    # Add index for Stripe customer lookups
    op.create_index(
        'idx_customers_stripe_customer',
        'customers',
        ['stripe_customer_id'],
        postgresql_concurrently=True,
        if_not_exists=True,
        unique=True
    )
    
    # Create partitioned table for usage_logs (by quarter)
    # Note: This requires manual data migration for existing data
    op.execute("""
        -- Create comment to document partitioning strategy
        COMMENT ON TABLE usage_logs IS 
        'Usage logs table. Consider partitioning by created_at for production deployments with high volume.
         Partitioning example:
         CREATE TABLE usage_logs_2025q4 PARTITION OF usage_logs
         FOR VALUES FROM (''2025-10-01'') TO (''2026-01-01'');';
    """)
    
    # Add statistics targets for better query planning
    op.execute("""
        ALTER TABLE usage_logs ALTER COLUMN customer_id SET STATISTICS 1000;
        ALTER TABLE usage_logs ALTER COLUMN package_id SET STATISTICS 1000;
        ALTER TABLE usage_logs ALTER COLUMN created_at SET STATISTICS 1000;
    """)
    
    op.execute("""
        ALTER TABLE deployments ALTER COLUMN customer_id SET STATISTICS 1000;
        ALTER TABLE deployments ALTER COLUMN status SET STATISTICS 500;
    """)
    
    # Analyze tables to update statistics
    op.execute("ANALYZE customers;")
    op.execute("ANALYZE deployments;")
    op.execute("ANALYZE usage_logs;")


def downgrade() -> None:
    """Remove performance optimizations"""
    
    # Drop indexes
    op.drop_index('idx_deployments_customer_status', table_name='deployments')
    op.drop_index('idx_deployments_customer_last_used', table_name='deployments')
    op.drop_index('idx_usage_logs_customer_created', table_name='usage_logs')
    op.drop_index('idx_usage_logs_package_created', table_name='usage_logs')
    op.drop_index('idx_usage_logs_status', table_name='usage_logs')
    op.drop_index('idx_customers_email_active', table_name='customers')
    op.drop_index('idx_customers_stripe_customer', table_name='customers')
    
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_usage_logs_metadata_gin;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_deployments_config_gin;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_customers_active;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_deployments_active;")
    
    # Reset statistics targets
    op.execute("""
        ALTER TABLE usage_logs ALTER COLUMN customer_id SET STATISTICS -1;
        ALTER TABLE usage_logs ALTER COLUMN package_id SET STATISTICS -1;
        ALTER TABLE usage_logs ALTER COLUMN created_at SET STATISTICS -1;
    """)
    
    op.execute("""
        ALTER TABLE deployments ALTER COLUMN customer_id SET STATISTICS -1;
        ALTER TABLE deployments ALTER COLUMN status SET STATISTICS -1;
    """)

