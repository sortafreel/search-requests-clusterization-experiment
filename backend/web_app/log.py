import logging
import logging.config
import os


def configure_logging() -> None:
    base_log_level = os.getenv("BASE_LOG_LEVEL", "INFO").upper()
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "verbose": {
                "format": "[%(asctime)s: %(levelname)s] [%(pathname)s:%(lineno)d] %(message)s (verbose - %(name)s)",
            },
        },
        "handlers": {
            "default": {
                "level": base_log_level,
                "formatter": "verbose",
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": base_log_level,
        },
        "loggers": {
            "": {"handlers": ["default"], "level": base_log_level, "propagate": True},
            "uvicorn.access": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }
    logging.config.dictConfig(logging_dict)
