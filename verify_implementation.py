#!/usr/bin/env python3
"""
Verification script - Check all implementations against Apex docs
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_imports():
    """Verify all imports work"""
    try:
        from apexomni.http_private_sign import HttpPrivateSign
        from apexomni.http_public import HttpPublic
        from apexomni.constants import APEX_OMNI_HTTP_MAIN, NETWORKID_OMNI_MAIN_ARB
        from apexomni.helpers.util import round_size
        
        from database import TradingDatabase
        from resilience import ResilientAPIClient, with_retry
        from logger_config import setup_structured_logging
        
        logger.info("✅ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def verify_database():
    """Verify database structure"""
    try:
        from database import TradingDatabase
        
        # Create test database
        db = TradingDatabase(db_path=":memory:")
        
        # Test operations
        db.start_cycle("test_cycle", {"test": "config"})
        db.end_cycle("test_cycle", 100.0, "TEST", 10)
        
        stats = db.get_performance_stats(30)
        
        db.close()
        
        logger.info("✅ Database module working")
        return True
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def verify_resilience():
    """Verify resilience module"""
    try:
        from resilience import RateLimiter, ExponentialBackoff, HealthChecker
        
        # Test rate limiter
        limiter = RateLimiter(max_requests=5, time_window=1)
        for _ in range(5):
            assert limiter.allow_request() == True
        
        # Test backoff
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=60.0)
        delay = backoff.get_delay(3)
        assert delay > 0
        
        # Test health checker
        checker = HealthChecker()
        checker.record_success(100.0)
        assert checker.is_healthy == True
        
        logger.info("✅ Resilience module working")
        return True
    except Exception as e:
        logger.error(f"❌ Resilience verification failed: {e}")
        return False

def verify_logger():
    """Verify logger configuration"""
    try:
        from logger_config import JSONFormatter, PerformanceMetrics
        
        # Test performance metrics
        metrics = PerformanceMetrics()
        metrics.record_metric('test', 100.0, 'ms')
        stats = metrics.get_stats('test')
        assert stats['count'] == 1
        
        logger.info("✅ Logger module working")
        return True
    except Exception as e:
        logger.error(f"❌ Logger verification failed: {e}")
        return False

def main():
    """Run all verifications"""
    logger.info("=" * 60)
    logger.info("🔍 VERIFYING IMPLEMENTATION")
    logger.info("=" * 60)
    logger.info("")
    
    results = []
    
    logger.info("1️⃣  Checking imports...")
    results.append(verify_imports())
    
    logger.info("")
    logger.info("2️⃣  Checking database...")
    results.append(verify_database())
    
    logger.info("")
    logger.info("3️⃣  Checking resilience...")
    results.append(verify_resilience())
    
    logger.info("")
    logger.info("4️⃣  Checking logger...")
    results.append(verify_logger())
    
    logger.info("")
    logger.info("=" * 60)
    
    if all(results):
        logger.info("✅ ALL VERIFICATIONS PASSED!")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("❌ SOME VERIFICATIONS FAILED")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
