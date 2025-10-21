"""Add execution history and usage aggregates tables

Revision ID: 20251021_0400
Revises: 20251021_0300
Create Date: 2025-10-21 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251021_0400'
down_revision = '20251021_0300'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add execution history and usage aggregates tables"""
    
    # Create execution_history table
    op.create_table(
        'execution_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('package_id', sa.String(100), nullable=False),
        sa.Column('package_name', sa.String(255), nullable=False),
        sa.Column('execution_type', sa.String(50), default='api'),
        sa.Column('input_data', postgresql.JSONB, nullable=True),
        sa.Column('output_data', postgresql.JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('input_tokens', sa.Integer, default=0),
        sa.Column('output_tokens', sa.Integer, default=0),
        sa.Column('total_tokens', sa.Integer, default=0),
        sa.Column('cost', sa.Float, default=0.0),
        sa.Column('duration_ms', sa.Integer, default=0),
        sa.Column('queue_time_ms', sa.Integer, default=0),
        sa.Column('customer_tier', sa.String(20), nullable=True),
        sa.Column('pricing_model', sa.String(50), default='per_execution'),
        sa.Column('api_key_used', sa.String(100), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    
    # Create indexes for execution_history
    op.create_index('idx_exec_id', 'execution_history', ['id'])
    op.create_index('idx_exec_customer', 'execution_history', ['customer_id'])
    op.create_index('idx_exec_package', 'execution_history', ['package_id'])
    op.create_index('idx_exec_status', 'execution_history', ['status'])
    op.create_index('idx_exec_created', 'execution_history', ['created_at'])
    op.create_index('idx_exec_customer_created', 'execution_history', ['customer_id', 'created_at'])
    op.create_index('idx_exec_package_created', 'execution_history', ['package_id', 'created_at'])
    op.create_index('idx_exec_status_created', 'execution_history', ['status', 'created_at'])
    op.create_index('idx_exec_customer_status', 'execution_history', ['customer_id', 'status'])
    op.create_index('idx_exec_tier_created', 'execution_history', ['customer_tier', 'created_at'])
    op.create_index('idx_exec_cost', 'execution_history', ['cost'])
    
    # Create GIN index for JSONB columns
    op.execute("""
        CREATE INDEX idx_exec_metadata_gin 
        ON execution_history USING gin (metadata jsonb_path_ops)
    """)
    
    op.execute("""
        CREATE INDEX idx_exec_input_gin 
        ON execution_history USING gin (input_data jsonb_path_ops)
    """)
    
    # Create usage_aggregates table
    op.create_table(
        'usage_aggregates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('package_id', sa.String(100), nullable=True),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_start', sa.DateTime, nullable=False),
        sa.Column('period_end', sa.DateTime, nullable=False),
        sa.Column('total_executions', sa.Integer, default=0),
        sa.Column('successful_executions', sa.Integer, default=0),
        sa.Column('failed_executions', sa.Integer, default=0),
        sa.Column('total_tokens', sa.Integer, default=0),
        sa.Column('total_cost', sa.Float, default=0.0),
        sa.Column('avg_duration_ms', sa.Integer, default=0),
        sa.Column('min_duration_ms', sa.Integer, default=0),
        sa.Column('max_duration_ms', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Create indexes for usage_aggregates
    op.create_index('idx_usage_agg_customer', 'usage_aggregates', ['customer_id'])
    op.create_index('idx_usage_agg_package', 'usage_aggregates', ['package_id'])
    op.create_index('idx_usage_agg_period', 'usage_aggregates', ['period_start', 'period_end'])
    op.create_index(
        'idx_usage_agg_unique',
        'usage_aggregates',
        ['customer_id', 'package_id', 'period_type', 'period_start'],
        unique=True
    )
    
    # Add table comments
    op.execute("""
        COMMENT ON TABLE execution_history IS 
        'Tracks all agent executions for billing, analytics, and audit purposes. 
         Consider partitioning by created_at for high-volume production deployments.';
    """)
    
    op.execute("""
        COMMENT ON TABLE usage_aggregates IS 
        'Pre-aggregated usage statistics for fast billing queries. 
         Updated by background jobs to avoid scanning execution_history.';
    """)
    
    # Add column comments
    op.execute("""
        COMMENT ON COLUMN execution_history.cost IS 'Execution cost in USD';
        COMMENT ON COLUMN execution_history.duration_ms IS 'Total execution time in milliseconds';
        COMMENT ON COLUMN execution_history.queue_time_ms IS 'Time spent waiting in queue';
        COMMENT ON COLUMN execution_history.customer_tier IS 'Customer tier at time of execution';
        COMMENT ON COLUMN execution_history.api_key_used IS 'API key identifier for BYOK tracking';
    """)
    
    # Create function to automatically update usage_aggregates
    op.execute("""
        CREATE OR REPLACE FUNCTION update_usage_aggregates()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update daily aggregate
            INSERT INTO usage_aggregates (
                id,
                customer_id,
                package_id,
                period_type,
                period_start,
                period_end,
                total_executions,
                successful_executions,
                failed_executions,
                total_tokens,
                total_cost,
                avg_duration_ms,
                min_duration_ms,
                max_duration_ms
            )
            VALUES (
                gen_random_uuid(),
                NEW.customer_id,
                NEW.package_id,
                'daily',
                date_trunc('day', NEW.created_at),
                date_trunc('day', NEW.created_at) + interval '1 day',
                1,
                CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END,
                CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
                NEW.total_tokens,
                NEW.cost,
                NEW.duration_ms,
                NEW.duration_ms,
                NEW.duration_ms
            )
            ON CONFLICT (customer_id, package_id, period_type, period_start)
            DO UPDATE SET
                total_executions = usage_aggregates.total_executions + 1,
                successful_executions = usage_aggregates.successful_executions + 
                    CASE WHEN NEW.status = 'success' THEN 1 ELSE 0 END,
                failed_executions = usage_aggregates.failed_executions + 
                    CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
                total_tokens = usage_aggregates.total_tokens + NEW.total_tokens,
                total_cost = usage_aggregates.total_cost + NEW.cost,
                avg_duration_ms = (usage_aggregates.avg_duration_ms * usage_aggregates.total_executions + NEW.duration_ms) / 
                    (usage_aggregates.total_executions + 1),
                min_duration_ms = LEAST(usage_aggregates.min_duration_ms, NEW.duration_ms),
                max_duration_ms = GREATEST(usage_aggregates.max_duration_ms, NEW.duration_ms),
                updated_at = NOW();
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to update aggregates
    op.execute("""
        CREATE TRIGGER trigger_update_usage_aggregates
        AFTER INSERT ON execution_history
        FOR EACH ROW
        EXECUTE FUNCTION update_usage_aggregates();
    """)
    
    # Set statistics for query optimization
    op.execute("""
        ALTER TABLE execution_history ALTER COLUMN customer_id SET STATISTICS 1000;
        ALTER TABLE execution_history ALTER COLUMN package_id SET STATISTICS 1000;
        ALTER TABLE execution_history ALTER COLUMN created_at SET STATISTICS 1000;
        ALTER TABLE execution_history ALTER COLUMN status SET STATISTICS 500;
    """)


def downgrade() -> None:
    """Remove execution history and usage aggregates tables"""
    
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_usage_aggregates ON execution_history;")
    op.execute("DROP FUNCTION IF EXISTS update_usage_aggregates();")
    
    # Drop tables
    op.drop_table('usage_aggregates')
    op.drop_table('execution_history')

