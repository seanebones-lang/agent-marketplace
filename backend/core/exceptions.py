"""
Production-Grade Exception Hierarchy for Agent Marketplace
Comprehensive error classification for proper handling and monitoring
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels for monitoring and alerting"""
    LOW = "low"  # Minor issues, doesn't affect user experience
    MEDIUM = "medium"  # Affects user experience but recoverable
    HIGH = "high"  # Critical error, requires immediate attention
    CRITICAL = "critical"  # System-wide failure, page ops team


class ErrorCategory(str, Enum):
    """Error categories for classification and metrics"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    RESOURCE_NOT_FOUND = "resource_not_found"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    AGENT_EXECUTION = "agent_execution"
    TIMEOUT = "timeout"
    CONFIGURATION = "configuration"
    INTERNAL = "internal"


class AgentMarketplaceException(Exception):
    """
    Base exception for all Agent Marketplace errors.
    
    Provides structured error information for logging, monitoring, and user feedback.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.retryable = retryable
        self.user_message = user_message or message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "retryable": self.retryable,
            "details": self.details
        }


# Authentication & Authorization Errors

class AuthenticationError(AgentMarketplaceException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTH_001",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=False,
            user_message="Authentication failed. Please check your credentials."
        )


class AuthorizationError(AgentMarketplaceException):
    """User not authorized for this action"""
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTH_002",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=False,
            user_message="You don't have permission to perform this action."
        )


class InvalidTokenError(AgentMarketplaceException):
    """Invalid or expired token"""
    def __init__(self, message: str = "Invalid or expired token", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTH_003",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=False,
            user_message="Your session has expired. Please log in again."
        )


# Rate Limiting Errors

class RateLimitExceededError(AgentMarketplaceException):
    """Rate limit exceeded"""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int = 0,
        reset_time: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"limit": limit, "reset_time": reset_time})
        super().__init__(
            message=message,
            error_code="RATE_001",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=True,
            user_message=f"Rate limit exceeded. Please try again in {reset_time} seconds."
        )


class ConcurrentLimitExceededError(AgentMarketplaceException):
    """Concurrent execution limit exceeded"""
    def __init__(
        self,
        message: str = "Concurrent execution limit exceeded",
        current: int = 0,
        limit: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"current": current, "limit": limit})
        super().__init__(
            message=message,
            error_code="RATE_002",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=True,
            user_message=f"You have {current} concurrent executions running. Maximum allowed: {limit}."
        )


class TokenLimitExceededError(AgentMarketplaceException):
    """Daily token limit exceeded"""
    def __init__(
        self,
        message: str = "Daily token limit exceeded",
        used: int = 0,
        limit: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"used": used, "limit": limit})
        super().__init__(
            message=message,
            error_code="RATE_003",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=False,
            user_message=f"Daily token limit exceeded ({used}/{limit}). Upgrade your plan or wait until tomorrow."
        )


# Validation Errors

class ValidationError(AgentMarketplaceException):
    """Input validation failed"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VAL_001",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=False,
            user_message=message
        )


class InvalidPackageError(AgentMarketplaceException):
    """Invalid or unknown agent package"""
    def __init__(self, package_id: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["package_id"] = package_id
        super().__init__(
            message=f"Invalid agent package: {package_id}",
            error_code="VAL_002",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=False,
            user_message=f"Agent package '{package_id}' not found."
        )


class InvalidTierError(AgentMarketplaceException):
    """Invalid model tier"""
    def __init__(self, tier: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["tier"] = tier
        super().__init__(
            message=f"Invalid model tier: {tier}",
            error_code="VAL_003",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=False,
            user_message=f"Model tier '{tier}' is not valid."
        )


# Resource Errors

class ResourceNotFoundError(AgentMarketplaceException):
    """Requested resource not found"""
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details.update({"resource_type": resource_type, "resource_id": resource_id})
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code="RES_001",
            category=ErrorCategory.RESOURCE_NOT_FOUND,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=False,
            user_message=f"{resource_type} not found."
        )


# External Service Errors

class ExternalServiceError(AgentMarketplaceException):
    """External service error (LLM provider, database, etc.)"""
    def __init__(
        self,
        service: str,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"service": service})
        if status_code:
            details["status_code"] = status_code
        super().__init__(
            message=f"{service} error: {message}",
            error_code="EXT_001",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            details=details,
            retryable=True,
            user_message=f"External service temporarily unavailable. Please try again."
        )


class LLMProviderError(ExternalServiceError):
    """LLM provider error (OpenAI, Anthropic, etc.)"""
    def __init__(
        self,
        provider: str,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service=f"LLM Provider ({provider})",
            message=message,
            status_code=status_code,
            details=details
        )
        self.error_code = "EXT_002"


class LLMRateLimitError(LLMProviderError):
    """LLM provider rate limit exceeded"""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            provider=provider,
            message="Rate limit exceeded",
            status_code=429,
            details=details
        )
        self.error_code = "EXT_003"
        self.retryable = True
        self.user_message = "LLM provider rate limit exceeded. Retrying automatically..."


class LLMQuotaExceededError(LLMProviderError):
    """LLM provider quota exceeded"""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            provider=provider,
            message="Quota exceeded",
            status_code=429,
            details=details
        )
        self.error_code = "EXT_004"
        self.retryable = False
        self.severity = ErrorSeverity.CRITICAL
        self.user_message = "LLM provider quota exceeded. Please contact support."


class LLMInvalidAPIKeyError(LLMProviderError):
    """Invalid LLM API key"""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            provider=provider,
            message="Invalid API key",
            status_code=401,
            details=details
        )
        self.error_code = "EXT_005"
        self.retryable = False
        self.severity = ErrorSeverity.CRITICAL
        self.user_message = "Invalid API key. Please check your configuration."


# Database Errors

class DatabaseError(AgentMarketplaceException):
    """Database operation error"""
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        super().__init__(
            message=message,
            error_code="DB_001",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details=details,
            retryable=True,
            user_message="Database error. Please try again."
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection failed"""
    def __init__(self, message: str = "Database connection failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, operation="connect", details=details)
        self.error_code = "DB_002"
        self.severity = ErrorSeverity.CRITICAL


class DatabaseTimeoutError(DatabaseError):
    """Database operation timeout"""
    def __init__(self, message: str = "Database operation timeout", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, operation="query", details=details)
        self.error_code = "DB_003"
        self.severity = ErrorSeverity.HIGH


# Agent Execution Errors

class AgentExecutionError(AgentMarketplaceException):
    """Agent execution failed"""
    def __init__(
        self,
        message: str,
        package_id: str,
        phase: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"package_id": package_id})
        if phase:
            details["phase"] = phase
        super().__init__(
            message=message,
            error_code="AGENT_001",
            category=ErrorCategory.AGENT_EXECUTION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=True,
            user_message="Agent execution failed. Please try again."
        )


class AgentTimeoutError(AgentMarketplaceException):
    """Agent execution timeout"""
    def __init__(
        self,
        package_id: str,
        timeout: int,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"package_id": package_id, "timeout": timeout})
        super().__init__(
            message=f"Agent execution timeout after {timeout}s",
            error_code="AGENT_002",
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=True,
            user_message=f"Agent execution exceeded {timeout}s timeout. Please try with a simpler task or upgrade your tier."
        )


class AgentConfigurationError(AgentMarketplaceException):
    """Agent configuration error"""
    def __init__(self, package_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["package_id"] = package_id
        super().__init__(
            message=message,
            error_code="AGENT_003",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            retryable=False,
            user_message="Agent configuration error. Please contact support."
        )


class AgentOutputValidationError(AgentMarketplaceException):
    """Agent output validation failed"""
    def __init__(self, package_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["package_id"] = package_id
        super().__init__(
            message=message,
            error_code="AGENT_004",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=True,
            user_message="Agent output validation failed. Retrying..."
        )


# Configuration Errors

class ConfigurationError(AgentMarketplaceException):
    """System configuration error"""
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(
            message=message,
            error_code="CFG_001",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            retryable=False,
            user_message="System configuration error. Please contact support."
        )


class MissingAPIKeyError(ConfigurationError):
    """Required API key not configured"""
    def __init__(self, provider: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["provider"] = provider
        super().__init__(
            message=f"Missing API key for {provider}",
            config_key=f"{provider.upper()}_API_KEY",
            details=details
        )
        self.error_code = "CFG_002"


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration value"""
    def __init__(self, config_key: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Invalid configuration for {config_key}: {message}",
            config_key=config_key,
            details=details
        )
        self.error_code = "CFG_003"


# Internal Errors

class InternalServerError(AgentMarketplaceException):
    """Internal server error"""
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="INT_001",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            retryable=True,
            user_message="An unexpected error occurred. Please try again or contact support."
        )


class CircuitBreakerOpenError(AgentMarketplaceException):
    """Circuit breaker is open"""
    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["service"] = service
        super().__init__(
            message=f"Circuit breaker open for {service}",
            error_code="INT_002",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            details=details,
            retryable=True,
            user_message=f"{service} is temporarily unavailable. Please try again in a few minutes."
        )


# Helper function to classify exceptions

def classify_exception(exc: Exception) -> AgentMarketplaceException:
    """
    Classify a generic exception into a specific AgentMarketplaceException.
    
    This is useful for wrapping third-party exceptions with our error hierarchy.
    """
    # Already classified
    if isinstance(exc, AgentMarketplaceException):
        return exc
    
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__
    
    # LLM provider errors
    if "anthropic" in exc_str or "openai" in exc_str or "groq" in exc_str:
        provider = "Anthropic" if "anthropic" in exc_str else "OpenAI" if "openai" in exc_str else "Groq"
        
        if "rate limit" in exc_str or "429" in exc_str:
            return LLMRateLimitError(provider, details={"original_error": str(exc)})
        elif "quota" in exc_str:
            return LLMQuotaExceededError(provider, details={"original_error": str(exc)})
        elif "api key" in exc_str or "401" in exc_str or "unauthorized" in exc_str:
            return LLMInvalidAPIKeyError(provider, details={"original_error": str(exc)})
        else:
            return LLMProviderError(provider, str(exc), details={"original_error": str(exc)})
    
    # Database errors
    if "database" in exc_str or "sqlalchemy" in exc_str or "psycopg" in exc_str:
        if "timeout" in exc_str:
            return DatabaseTimeoutError(str(exc), details={"original_error": str(exc)})
        elif "connection" in exc_str or "connect" in exc_str:
            return DatabaseConnectionError(str(exc), details={"original_error": str(exc)})
        else:
            return DatabaseError(str(exc), details={"original_error": str(exc)})
    
    # Timeout errors
    if exc_type == "TimeoutError" or "timeout" in exc_str:
        return AgentTimeoutError(
            package_id="unknown",
            timeout=300,
            details={"original_error": str(exc)}
        )
    
    # Validation errors
    if "validation" in exc_str or exc_type == "ValidationError":
        return ValidationError(str(exc), details={"original_error": str(exc)})
    
    # Default to internal server error
    return InternalServerError(
        message=f"Unhandled exception: {exc_type}",
        details={"original_error": str(exc), "exception_type": exc_type}
    )

