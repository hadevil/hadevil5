"""
Structured Logging Configuration
JSON logs with rotation, performance metrics, and audit trail
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import threading
import time


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted string
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class PerformanceMetrics:
    """Track and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, unit: str = ''):
        """
        Record a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = {
                    'values': [],
                    'unit': unit,
                    'count': 0,
                    'sum': 0,
                    'min': float('inf'),
                    'max': float('-inf')
                }
            
            metric = self.metrics[name]
            metric['values'].append(value)
            metric['count'] += 1
            metric['sum'] += value
            metric['min'] = min(metric['min'], value)
            metric['max'] = max(metric['max'], value)
            
            # Keep only last 1000 values
            if len(metric['values']) > 1000:
                metric['values'].pop(0)
    
    def get_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric
        
        Args:
            name: Metric name
            
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            if name not in self.metrics:
                return {}
            
            metric = self.metrics[name]
            values = metric['values']
            
            if not values:
                return {}
            
            return {
                'count': metric['count'],
                'sum': metric['sum'],
                'min': metric['min'],
                'max': metric['max'],
                'avg': metric['sum'] / metric['count'],
                'recent_avg': sum(values[-10:]) / min(len(values), 10) if values else 0,
                'unit': metric['unit']
            }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all metrics"""
        with self.lock:
            return {name: self.get_stats(name) for name in self.metrics.keys()}


class AuditLogger:
    """Audit trail logger for critical actions"""
    
    def __init__(self, log_file: str = 'logs/audit.log'):
        """
        Initialize audit logger
        
        Args:
            log_file: Path to audit log file
        """
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # Create logs directory
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log_action(self, action: str, details: Dict[str, Any], user: str = 'system'):
        """
        Log an auditable action
        
        Args:
            action: Action performed
            details: Action details
            user: User who performed action
        """
        log_data = {
            'action': action,
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        self.logger.info(json.dumps(log_data))


def setup_structured_logging(
    log_level: str = 'INFO',
    json_logs: bool = True,
    max_bytes: int = 50 * 1024 * 1024,  # 50MB
    backup_count: int = 10
):
    """
    Setup structured logging with JSON format and rotation
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON format for logs
        max_bytes: Maximum size per log file
        backup_count: Number of backup files to keep
    """
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # File handlers
    json_log_file = logs_dir / f'bot_{timestamp}.json'
    text_log_file = logs_dir / f'bot_{timestamp}.log'
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # JSON file handler
    if json_logs:
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)  # Log everything to JSON
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)
    
    # Text file handler (backup/human-readable)
    text_handler = logging.handlers.RotatingFileHandler(
        text_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    text_handler.setLevel(getattr(logging, log_level.upper()))
    text_handler.setFormatter(console_formatter)
    root_logger.addHandler(text_handler)
    
    # Set levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("🚀 STRUCTURED LOGGING INITIALIZED")
    logger.info("=" * 80)
    logger.info(f"📝 JSON logs: {json_log_file}")
    logger.info(f"📝 Text logs: {text_log_file}")
    logger.info(f"📊 Log level: {log_level}")
    logger.info(f"🔄 Max file size: {max_bytes / (1024 * 1024):.0f} MB")
    logger.info(f"📦 Backup count: {backup_count}")
    logger.info("=" * 80)
    logger.info("")


class PerformanceLogger:
    """Context manager for logging function performance"""
    
    def __init__(self, operation: str, metrics: PerformanceMetrics):
        """
        Initialize performance logger
        
        Args:
            operation: Name of operation being timed
            metrics: PerformanceMetrics instance
        """
        self.operation = operation
        self.metrics = metrics
        self.start_time = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log"""
        duration_ms = (time.time() - self.start_time) * 1000
        
        self.metrics.record_metric(f'{self.operation}_duration', duration_ms, 'ms')
        
        if exc_type is None:
            self.logger.debug(f"⏱️  {self.operation} completed in {duration_ms:.2f}ms")
        else:
            self.logger.warning(f"⏱️  {self.operation} failed after {duration_ms:.2f}ms: {exc_val}")


# Global instances
performance_metrics = PerformanceMetrics()
audit_logger = AuditLogger()
