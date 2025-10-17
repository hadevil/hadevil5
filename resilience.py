"""
Resilience Module - API reliability and fault tolerance
Handles reconnection, rate limiting, exponential backoff, health checks
"""

import time
import logging
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 1):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def allow_request(self) -> bool:
        """
        Check if request is allowed
        
        Returns:
            True if request allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def wait_if_needed(self):
        """Block until request is allowed"""
        while not self.allow_request():
            time.sleep(0.1)


class ExponentialBackoff:
    """Exponential backoff strategy for retries"""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, max_retries: int = 5):
        """
        Initialize backoff strategy
        
        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            max_retries: Maximum number of retries
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt
        
        Args:
            attempt: Retry attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay


def with_retry(max_retries: int = 3, base_delay: float = 1.0, 
               exceptions: tuple = (Exception,), on_failure: Optional[Callable] = None):
    """
    Decorator to retry function with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries
        exceptions: Tuple of exceptions to catch
        on_failure: Callback function on final failure
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            backoff = ExponentialBackoff(base_delay=base_delay, max_retries=max_retries)
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_retries:
                        logger.error(f"❌ {func.__name__} failed after {max_retries} retries: {e}")
                        if on_failure:
                            on_failure(e)
                        raise
                    
                    delay = backoff.get_delay(attempt)
                    logger.warning(f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                                 f"retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator


class HealthChecker:
    """Monitor API health and connectivity"""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize health checker
        
        Args:
            check_interval: Interval between health checks in seconds
        """
        self.check_interval = check_interval
        self.last_check_time = None
        self.is_healthy = True
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.api_response_times = []
        self.max_response_time_samples = 100
    
    def record_success(self, response_time_ms: float):
        """
        Record successful API call
        
        Args:
            response_time_ms: Response time in milliseconds
        """
        self.last_check_time = datetime.now()
        self.is_healthy = True
        self.consecutive_failures = 0
        
        # Track response times
        self.api_response_times.append(response_time_ms)
        if len(self.api_response_times) > self.max_response_time_samples:
            self.api_response_times.pop(0)
    
    def record_failure(self, error: Exception):
        """
        Record failed API call
        
        Args:
            error: Exception that occurred
        """
        self.last_check_time = datetime.now()
        self.consecutive_failures += 1
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.is_healthy = False
            logger.error(f"🚨 API marked as UNHEALTHY after {self.consecutive_failures} failures")
    
    def needs_check(self) -> bool:
        """
        Check if health check is needed
        
        Returns:
            True if check needed
        """
        if not self.last_check_time:
            return True
        
        elapsed = (datetime.now() - self.last_check_time).total_seconds()
        return elapsed >= self.check_interval
    
    def get_avg_response_time(self) -> Optional[float]:
        """
        Get average API response time
        
        Returns:
            Average response time in milliseconds or None
        """
        if not self.api_response_times:
            return None
        return sum(self.api_response_times) / len(self.api_response_times)
    
    def get_status(self) -> dict:
        """
        Get health status
        
        Returns:
            Dictionary with health status
        """
        return {
            'is_healthy': self.is_healthy,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'consecutive_failures': self.consecutive_failures,
            'avg_response_time_ms': self.get_avg_response_time()
        }


class CircuitBreaker:
    """Circuit breaker pattern for API calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is OPEN
        """
        with self.lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info("🔄 Circuit breaker: HALF_OPEN, attempting recovery")
                else:
                    raise Exception("Circuit breaker is OPEN - API calls blocked")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit"""
        if not self.last_failure_time:
            return False
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == 'HALF_OPEN':
            logger.info("✅ Circuit breaker: CLOSED, recovery successful")
        
        self.failure_count = 0
        self.state = 'CLOSED'
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"🚨 Circuit breaker: OPEN after {self.failure_count} failures")
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state


class ResilientAPIClient:
    """Wrapper for API client with full resilience"""
    
    def __init__(self, base_client, rate_limit: int = 10):
        """
        Initialize resilient client
        
        Args:
            base_client: Base API client to wrap
            rate_limit: Maximum requests per second
        """
        self.base_client = base_client
        self.rate_limiter = RateLimiter(max_requests=rate_limit, time_window=1)
        self.health_checker = HealthChecker(check_interval=60)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    
    def call(self, method_name: str, *args, **kwargs) -> Any:
        """
        Make API call with full resilience
        
        Args:
            method_name: Name of method to call on base client
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Method result
        """
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Get method
        method = getattr(self.base_client, method_name)
        
        # Execute with retry and circuit breaker
        start_time = time.time()
        
        try:
            result = self.circuit_breaker.call(method, *args, **kwargs)
            
            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            self.health_checker.record_success(response_time_ms)
            
            return result
        except Exception as e:
            # Record failure
            self.health_checker.record_failure(e)
            raise
    
    def get_health_status(self) -> dict:
        """Get current health status"""
        health_status = self.health_checker.get_status()
        health_status['circuit_breaker_state'] = self.circuit_breaker.get_state()
        return health_status
