import logging

LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(levelname)s\t%(asctime)s  %(message)s'
}

logging.basicConfig(**LOGGING_CONFIG)
