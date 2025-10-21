"""
Tests for Configuration Module

This module tests the configuration settings.
"""

import pytest
from core.config import Settings


class TestSettings:
    """Test suite for application settings"""
    
    def test_settings_initialization(self):
        """Test that settings can be initialized"""
        settings = Settings()
        
        assert settings is not None
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'REDIS_URL')
        assert hasattr(settings, 'SECRET_KEY')
    
    def test_database_url_format(self):
        """Test database URL has correct format"""
        settings = Settings()
        
        assert settings.DATABASE_URL.startswith('postgresql://')
    
    def test_redis_url_format(self):
        """Test Redis URL has correct format"""
        settings = Settings()
        
        assert settings.REDIS_URL.startswith('redis://')
    
    def test_environment_defaults(self):
        """Test default environment values"""
        settings = Settings()
        
        assert settings.ENVIRONMENT in ['development', 'staging', 'production']
        assert isinstance(settings.DEBUG, bool)
        assert settings.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR']

