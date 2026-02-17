import logging
import os
from datetime import datetime


class LoggerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Create logger with specific name
        self.logger = logging.getLogger("connectly_api")
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler for persistent logging
        log_file = os.path.join(log_dir, 'api.log')
        file_handler = logging.FileHandler(log_file)
        
        # Create console handler for development
        console_handler = logging.StreamHandler()
        
        # Set up formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Set logging level
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False

    def get_logger(self):
        return self.logger

    def log_api_request(self, method, endpoint, user=None, status_code=None):
        """Log API requests with structured information"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'user': user.username if user else 'Anonymous',
            'status_code': status_code
        }
        
        if status_code and status_code >= 400:
            self.logger.error(f"API Error: {log_data}")
        else:
            self.logger.info(f"API Request: {log_data}")

    def log_security_event(self, event_type, details, user=None):
        """Log security-related events"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'user': user.username if user else 'Anonymous'
        }
        
        self.logger.warning(f"Security Event: {log_data}")

    def log_performance_metric(self, metric_name, value, details=None):
        """Log performance metrics"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
            'details': details
        }
        
        self.logger.info(f"Performance: {log_data}")

    def set_log_level(self, level):
        """Dynamically change log level"""
        self.logger.setLevel(level)
