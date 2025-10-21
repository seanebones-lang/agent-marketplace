"""
Multi-Tenancy Isolation with Row-Level Security
Provides tenant context and database isolation
"""

import logging
from typing import Optional
from contextvars import ContextVar
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Context variable for current tenant
current_tenant_id: ContextVar[Optional[str]] = ContextVar('current_tenant_id', default=None)


class TenantContext:
    """
    Manages tenant context for multi-tenancy isolation
    """
    
    def __init__(self):
        self.current_tenant: Optional[str] = None
        self.vector_namespace: str = ""
        self.redis_prefix: str = ""
    
    def set_tenant(self, customer_id: str):
        """
        Set the current tenant context
        
        Args:
            customer_id: Customer/tenant identifier
        """
        self.current_tenant = customer_id
        self.vector_namespace = f"tenant_{customer_id}"
        self.redis_prefix = f"tenant:{customer_id}"
        
        # Set context variable for async contexts
        current_tenant_id.set(customer_id)
        
        logger.debug(f"Tenant context set to: {customer_id}")
    
    def clear_tenant(self):
        """Clear the current tenant context"""
        self.current_tenant = None
        self.vector_namespace = ""
        self.redis_prefix = ""
        current_tenant_id.set(None)
        
        logger.debug("Tenant context cleared")
    
    def get_tenant(self) -> Optional[str]:
        """Get the current tenant ID"""
        return self.current_tenant or current_tenant_id.get()
    
    def get_vector_namespace(self) -> str:
        """Get the vector database namespace for current tenant"""
        tenant_id = self.get_tenant()
        return f"tenant_{tenant_id}" if tenant_id else "default"
    
    def get_redis_key(self, key: str) -> str:
        """Get tenant-prefixed Redis key"""
        tenant_id = self.get_tenant()
        if tenant_id:
            return f"tenant:{tenant_id}:{key}"
        return key
    
    def ensure_tenant(self):
        """Ensure tenant context is set, raise error if not"""
        if not self.get_tenant():
            raise RuntimeError("Tenant context not set")


# Global tenant context instance
_tenant_context = TenantContext()


def get_tenant_context() -> TenantContext:
    """Get global tenant context instance"""
    return _tenant_context


def setup_row_level_security(engine: Engine):
    """
    Setup Row-Level Security policies for PostgreSQL
    
    Args:
        engine: SQLAlchemy engine
    """
    
    @event.listens_for(Session, "after_begin")
    def receive_after_begin(session, transaction, connection):
        """Set RLS policy for each session"""
        tenant_id = current_tenant_id.get()
        
        if tenant_id:
            # Set session variable for RLS policy
            connection.execute(
                text("SET LOCAL app.current_tenant_id = :tenant_id"),
                {"tenant_id": tenant_id}
            )
            logger.debug(f"RLS policy set for tenant: {tenant_id}")
    
    # Create RLS policies (run once during setup)
    with engine.connect() as conn:
        try:
            # Enable RLS on tables
            conn.execute(text("ALTER TABLE deployments ENABLE ROW LEVEL SECURITY;"))
            conn.execute(text("ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;"))
            
            # Create policy for deployments
            conn.execute(text("""
                DROP POLICY IF EXISTS tenant_isolation_policy ON deployments;
            """))
            
            conn.execute(text("""
                CREATE POLICY tenant_isolation_policy ON deployments
                USING (customer_id = CAST(current_setting('app.current_tenant_id', TRUE) AS INTEGER))
                WITH CHECK (customer_id = CAST(current_setting('app.current_tenant_id', TRUE) AS INTEGER));
            """))
            
            # Create policy for usage_logs
            conn.execute(text("""
                DROP POLICY IF EXISTS tenant_isolation_policy ON usage_logs;
            """))
            
            conn.execute(text("""
                CREATE POLICY tenant_isolation_policy ON usage_logs
                USING (customer_id = CAST(current_setting('app.current_tenant_id', TRUE) AS INTEGER))
                WITH CHECK (customer_id = CAST(current_setting('app.current_tenant_id', TRUE) AS INTEGER));
            """))
            
            # Create bypass policy for superuser/admin operations
            conn.execute(text("""
                DROP POLICY IF EXISTS bypass_rls_policy ON deployments;
            """))
            
            conn.execute(text("""
                CREATE POLICY bypass_rls_policy ON deployments
                USING (current_setting('app.bypass_rls', TRUE) = 'true');
            """))
            
            conn.execute(text("""
                DROP POLICY IF EXISTS bypass_rls_policy ON usage_logs;
            """))
            
            conn.execute(text("""
                CREATE POLICY bypass_rls_policy ON usage_logs
                USING (current_setting('app.bypass_rls', TRUE) = 'true');
            """))
            
            conn.commit()
            logger.info("Row-Level Security policies created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup RLS policies: {e}")
            conn.rollback()


def bypass_rls(session: Session):
    """
    Context manager to bypass RLS for admin operations
    
    Usage:
        with bypass_rls(session):
            # Admin queries that need to see all tenants
            all_deployments = session.query(Deployment).all()
    """
    class RLSBypass:
        def __enter__(self):
            session.execute(text("SET LOCAL app.bypass_rls = 'true';"))
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            session.execute(text("SET LOCAL app.bypass_rls = 'false';"))
    
    return RLSBypass()


class TenantIsolationMiddleware:
    """
    Middleware to set tenant context from request
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract tenant ID from request (e.g., from auth token)
            # This would be set by your authentication middleware
            request = scope.get("request")
            if request and hasattr(request.state, "customer_id"):
                tenant_context = get_tenant_context()
                tenant_context.set_tenant(str(request.state.customer_id))
        
        try:
            await self.app(scope, receive, send)
        finally:
            # Clear tenant context after request
            tenant_context = get_tenant_context()
            tenant_context.clear_tenant()


# Example usage
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create engine
    engine = create_engine("postgresql://user:pass@localhost/db")
    
    # Setup RLS
    setup_row_level_security(engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Set tenant context
    tenant_context = get_tenant_context()
    tenant_context.set_tenant("customer_123")
    
    # All queries will now be filtered by tenant
    # deployments = session.query(Deployment).all()  # Only sees customer_123's data
    
    # Admin operation - bypass RLS
    with bypass_rls(session):
        # all_deployments = session.query(Deployment).all()  # Sees all tenants
        pass
    
    # Clear tenant context
    tenant_context.clear_tenant()

