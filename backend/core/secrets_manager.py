"""
Secrets Management with HashiCorp Vault Integration
Provides secure secret storage and retrieval for production environments
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
import hvac
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VaultConfig(BaseModel):
    """Vault configuration settings"""
    url: str = Field(default_factory=lambda: os.getenv("VAULT_ADDR", "http://localhost:8200"))
    token: Optional[str] = Field(default_factory=lambda: os.getenv("VAULT_TOKEN"))
    namespace: Optional[str] = Field(default_factory=lambda: os.getenv("VAULT_NAMESPACE"))
    mount_point: str = Field(default="secret")
    enabled: bool = Field(default_factory=lambda: os.getenv("VAULT_ENABLED", "false").lower() == "true")


class SecretsManager:
    """
    Centralized secrets management with Vault integration
    Falls back to environment variables if Vault is not enabled
    """
    
    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self.client: Optional[hvac.Client] = None
        self._cache: Dict[str, Any] = {}
        
        if self.config.enabled:
            self._initialize_vault()
        else:
            logger.info("Vault integration disabled, using environment variables")
    
    def _initialize_vault(self):
        """Initialize Vault client with authentication"""
        try:
            self.client = hvac.Client(
                url=self.config.url,
                token=self.config.token,
                namespace=self.config.namespace
            )
            
            if not self.client.is_authenticated():
                logger.error("Vault authentication failed")
                self.client = None
            else:
                logger.info(f"Successfully connected to Vault at {self.config.url}")
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            self.client = None
    
    def get_secret(self, path: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Retrieve secret from Vault or environment
        
        Args:
            path: Secret path (e.g., "database/credentials")
            key: Specific key within the secret (optional)
            default: Default value if secret not found
        
        Returns:
            Secret value or default
        """
        cache_key = f"{path}:{key}" if key else path
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try Vault if enabled
        if self.config.enabled and self.client:
            try:
                secret_data = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point=self.config.mount_point
                )
                
                data = secret_data['data']['data']
                value = data.get(key) if key else data
                
                # Cache the result
                self._cache[cache_key] = value
                return value
            
            except Exception as e:
                logger.warning(f"Failed to retrieve secret from Vault: {e}")
        
        # Fallback to environment variables
        env_key = path.upper().replace("/", "_")
        if key:
            env_key = f"{env_key}_{key.upper()}"
        
        value = os.getenv(env_key, default)
        self._cache[cache_key] = value
        return value
    
    def set_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Store secret in Vault
        
        Args:
            path: Secret path
            data: Secret data dictionary
        
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.client:
            logger.warning("Vault not enabled, cannot store secret")
            return False
        
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point=self.config.mount_point
            )
            
            # Invalidate cache for this path
            self._invalidate_cache(path)
            
            logger.info(f"Successfully stored secret at {path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store secret in Vault: {e}")
            return False
    
    def delete_secret(self, path: str) -> bool:
        """Delete secret from Vault"""
        if not self.config.enabled or not self.client:
            return False
        
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.config.mount_point
            )
            
            self._invalidate_cache(path)
            logger.info(f"Successfully deleted secret at {path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete secret from Vault: {e}")
            return False
    
    def _invalidate_cache(self, path: str):
        """Invalidate cache entries for a given path"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(path)]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_cache(self):
        """Clear all cached secrets"""
        self._cache.clear()
        logger.info("Secrets cache cleared")


@lru_cache()
def get_secrets_manager() -> SecretsManager:
    """Get singleton instance of SecretsManager"""
    return SecretsManager()


def mask_secret(value: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging
    
    Args:
        value: Secret value to mask
        visible_chars: Number of characters to show at the end
    
    Returns:
        Masked string (e.g., "sk-...xyz123")
    """
    if not value or len(value) <= visible_chars:
        return "***"
    
    return f"{value[:3]}...{value[-visible_chars:]}"


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize dictionary for safe logging by masking sensitive fields
    
    Args:
        data: Dictionary potentially containing sensitive data
    
    Returns:
        Sanitized dictionary with masked sensitive fields
    """
    sensitive_keys = {
        'password', 'token', 'api_key', 'secret', 'apikey',
        'authorization', 'auth', 'credential', 'private_key',
        'stripe_key', 'openai_key', 'anthropic_key'
    }
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if key contains sensitive terms
        is_sensitive = any(term in key_lower for term in sensitive_keys)
        
        if is_sensitive and isinstance(value, str):
            sanitized[key] = mask_secret(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_log_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


# Example usage
if __name__ == "__main__":
    # Initialize secrets manager
    secrets = get_secrets_manager()
    
    # Retrieve secrets
    db_password = secrets.get_secret("database/credentials", "password")
    openai_key = secrets.get_secret("llm/openai", "api_key")
    
    # Store secrets (Vault only)
    secrets.set_secret("app/config", {
        "debug": "false",
        "log_level": "INFO"
    })
    
    # Mask sensitive data for logging
    print(mask_secret("sk-1234567890abcdef"))  # Output: sk-...cdef
    
    # Sanitize log data
    log_data = {
        "user_id": 123,
        "api_key": "secret-key-12345",
        "email": "user@example.com"
    }
    print(sanitize_log_data(log_data))
    # Output: {'user_id': 123, 'api_key': 'sec...2345', 'email': 'user@example.com'}

