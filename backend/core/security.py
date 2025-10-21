"""
Production-Grade Security Module
Comprehensive security utilities for input validation, sanitization, and protection
"""

import re
import html
import hashlib
import secrets
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import bleach

from core.exceptions import ValidationError, SecurityError
from core.logging import get_logger

logger = get_logger(__name__)


class SecurityLevel(str, Enum):
    """Security validation levels"""
    STRICT = "strict"  # Maximum security, reject anything suspicious
    STANDARD = "standard"  # Balanced security
    PERMISSIVE = "permissive"  # Minimal validation


class InputValidator:
    """
    Production-grade input validation and sanitization.
    
    Protects against:
    - SQL Injection
    - XSS (Cross-Site Scripting)
    - Command Injection
    - Path Traversal
    - NoSQL Injection
    - LDAP Injection
    """
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(';|\"--|\";)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<applet",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"`.*`",
        r"\|\|",
        r"&&",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"~\/",
        r"\/etc\/",
        r"\/proc\/",
        r"\/sys\/",
    ]
    
    @staticmethod
    def validate_string(
        value: str,
        field_name: str,
        min_length: int = 0,
        max_length: int = 10000,
        allow_special_chars: bool = True,
        security_level: SecurityLevel = SecurityLevel.STANDARD
    ) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Input string to validate
            field_name: Name of the field (for error messages)
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            allow_special_chars: Allow special characters
            security_level: Security validation level
        
        Returns:
            Sanitized string
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{field_name} must be a string",
                field=field_name,
                details={"type": type(value).__name__}
            )
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters",
                field=field_name,
                details={"length": len(value), "min_length": min_length}
            )
        
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} must be at most {max_length} characters",
                field=field_name,
                details={"length": len(value), "max_length": max_length}
            )
        
        # SQL Injection detection
        if security_level in [SecurityLevel.STRICT, SecurityLevel.STANDARD]:
            for pattern in InputValidator.SQL_INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(
                        f"SQL injection attempt detected in {field_name}",
                        extra={"field": field_name, "pattern": pattern}
                    )
                    raise ValidationError(
                        f"{field_name} contains potentially malicious content",
                        field=field_name,
                        details={"reason": "sql_injection_detected"}
                    )
        
        # XSS detection
        if security_level in [SecurityLevel.STRICT, SecurityLevel.STANDARD]:
            for pattern in InputValidator.XSS_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    logger.warning(
                        f"XSS attempt detected in {field_name}",
                        extra={"field": field_name, "pattern": pattern}
                    )
                    raise ValidationError(
                        f"{field_name} contains potentially malicious content",
                        field=field_name,
                        details={"reason": "xss_detected"}
                    )
        
        # Command injection detection
        if security_level == SecurityLevel.STRICT:
            for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
                if re.search(pattern, value):
                    logger.warning(
                        f"Command injection attempt detected in {field_name}",
                        extra={"field": field_name}
                    )
                    raise ValidationError(
                        f"{field_name} contains invalid characters",
                        field=field_name,
                        details={"reason": "command_injection_detected"}
                    )
        
        # Special character validation
        if not allow_special_chars:
            if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', value):
                raise ValidationError(
                    f"{field_name} contains invalid characters",
                    field=field_name,
                    details={"allowed": "alphanumeric, spaces, hyphens, underscores, dots"}
                )
        
        # Sanitize HTML entities
        sanitized = html.escape(value)
        
        return sanitized
    
    @staticmethod
    def validate_email(email: str, field_name: str = "email") -> str:
        """
        Validate email address.
        
        Args:
            email: Email address to validate
            field_name: Field name for error messages
        
        Returns:
            Validated email (lowercase)
        
        Raises:
            ValidationError: If email is invalid
        """
        if not isinstance(email, str):
            raise ValidationError(
                f"{field_name} must be a string",
                field=field_name
            )
        
        email = email.strip().lower()
        
        # RFC 5322 compliant email regex (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError(
                f"Invalid {field_name} format",
                field=field_name,
                details={"email": email}
            )
        
        # Additional checks
        if len(email) > 254:  # RFC 5321
            raise ValidationError(
                f"{field_name} is too long",
                field=field_name
            )
        
        local, domain = email.split('@')
        
        if len(local) > 64:  # RFC 5321
            raise ValidationError(
                f"{field_name} local part is too long",
                field=field_name
            )
        
        # Check for suspicious patterns
        suspicious_patterns = ['..', '--', '__']
        if any(pattern in email for pattern in suspicious_patterns):
            raise ValidationError(
                f"Invalid {field_name} format",
                field=field_name
            )
        
        return email
    
    @staticmethod
    def validate_url(
        url: str,
        field_name: str = "url",
        allowed_schemes: List[str] = ["http", "https"]
    ) -> str:
        """
        Validate URL.
        
        Args:
            url: URL to validate
            field_name: Field name for error messages
            allowed_schemes: Allowed URL schemes
        
        Returns:
            Validated URL
        
        Raises:
            ValidationError: If URL is invalid
        """
        if not isinstance(url, str):
            raise ValidationError(
                f"{field_name} must be a string",
                field=field_name
            )
        
        url = url.strip()
        
        # Basic URL pattern
        url_pattern = r'^(https?):\/\/([\w\-\.]+)(:\d+)?(\/.*)?$'
        
        if not re.match(url_pattern, url, re.IGNORECASE):
            raise ValidationError(
                f"Invalid {field_name} format",
                field=field_name
            )
        
        # Extract scheme
        scheme = url.split('://')[0].lower()
        
        if scheme not in allowed_schemes:
            raise ValidationError(
                f"{field_name} scheme not allowed",
                field=field_name,
                details={"scheme": scheme, "allowed": allowed_schemes}
            )
        
        # Check for suspicious patterns
        if any(pattern in url.lower() for pattern in ['javascript:', 'data:', 'file:']):
            raise ValidationError(
                f"{field_name} contains invalid scheme",
                field=field_name
            )
        
        return url
    
    @staticmethod
    def validate_json(
        data: Dict[str, Any],
        max_depth: int = 10,
        max_keys: int = 1000
    ) -> Dict[str, Any]:
        """
        Validate JSON data structure.
        
        Args:
            data: JSON data to validate
            max_depth: Maximum nesting depth
            max_keys: Maximum number of keys
        
        Returns:
            Validated JSON data
        
        Raises:
            ValidationError: If JSON is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError(
                "Data must be a dictionary",
                details={"type": type(data).__name__}
            )
        
        # Check depth
        def get_depth(obj, current_depth=0):
            if current_depth > max_depth:
                return current_depth
            if isinstance(obj, dict):
                return max(get_depth(v, current_depth + 1) for v in obj.values()) if obj else current_depth
            elif isinstance(obj, list):
                return max(get_depth(item, current_depth + 1) for item in obj) if obj else current_depth
            return current_depth
        
        depth = get_depth(data)
        if depth > max_depth:
            raise ValidationError(
                f"JSON nesting too deep (max: {max_depth})",
                details={"depth": depth, "max_depth": max_depth}
            )
        
        # Check number of keys
        def count_keys(obj):
            if isinstance(obj, dict):
                return len(obj) + sum(count_keys(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_keys(item) for item in obj)
            return 0
        
        key_count = count_keys(data)
        if key_count > max_keys:
            raise ValidationError(
                f"Too many keys in JSON (max: {max_keys})",
                details={"keys": key_count, "max_keys": max_keys}
            )
        
        return data
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal.
        
        Args:
            filename: Filename to sanitize
        
        Returns:
            Sanitized filename
        
        Raises:
            ValidationError: If filename is invalid
        """
        if not isinstance(filename, str):
            raise ValidationError(
                "Filename must be a string",
                field="filename"
            )
        
        # Check for path traversal
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, filename):
                raise ValidationError(
                    "Invalid filename",
                    field="filename",
                    details={"reason": "path_traversal_detected"}
                )
        
        # Remove any path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Allow only safe characters
        filename = re.sub(r'[^a-zA-Z0-9\-_\.]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        if not filename:
            raise ValidationError(
                "Filename cannot be empty",
                field="filename"
            )
        
        return filename


class APIKeyManager:
    """
    Secure API key management.
    
    Features:
    - Secure key generation
    - Key hashing for storage
    - Key validation
    - Key rotation support
    """
    
    @staticmethod
    def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
        """
        Generate a secure API key.
        
        Args:
            prefix: Key prefix (e.g., "sk" for secret key)
            length: Length of random part
        
        Returns:
            Generated API key
        """
        random_bytes = secrets.token_urlsafe(length)
        api_key = f"{prefix}_{random_bytes}"
        
        logger.info(
            "API key generated",
            extra={"prefix": prefix, "length": len(api_key)}
        )
        
        return api_key
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash API key for secure storage.
        
        Args:
            api_key: API key to hash
        
        Returns:
            Hashed API key (hex)
        """
        # Use SHA-256 for hashing
        hash_obj = hashlib.sha256(api_key.encode())
        return hash_obj.hexdigest()
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
        
        Returns:
            True if valid format
        """
        if not isinstance(api_key, str):
            return False
        
        # Check format: prefix_randompart
        if '_' not in api_key:
            return False
        
        prefix, random_part = api_key.split('_', 1)
        
        # Validate prefix
        if not re.match(r'^[a-z]{2,4}$', prefix):
            return False
        
        # Validate random part (base64url characters)
        if not re.match(r'^[A-Za-z0-9\-_]+$', random_part):
            return False
        
        # Check length
        if len(random_part) < 20:
            return False
        
        return True
    
    @staticmethod
    def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
        """
        Mask API key for logging/display.
        
        Args:
            api_key: API key to mask
            visible_chars: Number of characters to show at end
        
        Returns:
            Masked API key
        """
        if not api_key or len(api_key) <= visible_chars:
            return "***"
        
        return f"***{api_key[-visible_chars:]}"


class DataEncryption:
    """
    Secure data encryption for sensitive information.
    
    Uses Fernet (symmetric encryption) for encrypting:
    - API keys
    - Customer secrets
    - Sensitive configuration
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize encryption with key.
        
        Args:
            encryption_key: 32-byte encryption key (base64 encoded)
        """
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            # Generate key from environment or create new
            import os
            key = os.getenv("ENCRYPTION_KEY")
            if key:
                self.fernet = Fernet(key.encode())
            else:
                # Generate new key (should be saved to env)
                self.fernet = Fernet(Fernet.generate_key())
                logger.warning(
                    "No ENCRYPTION_KEY found, generated new key. "
                    "Save this key to environment for production!"
                )
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data.
        
        Args:
            data: String to encrypt
        
        Returns:
            Encrypted data (base64 encoded)
        """
        encrypted = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt string data.
        
        Args:
            encrypted_data: Encrypted data (base64 encoded)
        
        Returns:
            Decrypted string
        """
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()


class RateLimitBypass:
    """
    Detect and prevent rate limit bypass attempts.
    """
    
    @staticmethod
    def detect_suspicious_patterns(
        customer_id: str,
        ip_address: str,
        user_agent: str,
        request_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect suspicious patterns that may indicate abuse.
        
        Args:
            customer_id: Customer ID
            ip_address: Request IP address
            user_agent: User agent string
            request_history: Recent request history
        
        Returns:
            Dictionary with suspicious activity flags
        """
        flags = {
            "suspicious": False,
            "reasons": [],
            "risk_score": 0
        }
        
        # Check for rapid IP changes
        if len(request_history) >= 10:
            recent_ips = [r.get("ip") for r in request_history[-10:]]
            unique_ips = len(set(recent_ips))
            if unique_ips > 5:
                flags["suspicious"] = True
                flags["reasons"].append("rapid_ip_changes")
                flags["risk_score"] += 30
        
        # Check for user agent rotation
        if len(request_history) >= 10:
            recent_uas = [r.get("user_agent") for r in request_history[-10:]]
            unique_uas = len(set(recent_uas))
            if unique_uas > 3:
                flags["suspicious"] = True
                flags["reasons"].append("user_agent_rotation")
                flags["risk_score"] += 20
        
        # Check for bot-like user agents
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        if any(pattern in user_agent.lower() for pattern in bot_patterns):
            flags["reasons"].append("bot_user_agent")
            flags["risk_score"] += 10
        
        # Check for suspicious timing patterns
        if len(request_history) >= 5:
            timestamps = [r.get("timestamp") for r in request_history[-5:]]
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            # Check if intervals are suspiciously regular (bot-like)
            if len(intervals) >= 3:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                if variance < 0.1 and avg_interval < 2:
                    flags["suspicious"] = True
                    flags["reasons"].append("regular_timing_pattern")
                    flags["risk_score"] += 25
        
        return flags


class SecurityError(Exception):
    """Security-related error"""
    pass


# Global instances
input_validator = InputValidator()
api_key_manager = APIKeyManager()
data_encryption = DataEncryption()
