from gunicorn import glogging
from uvicorn.workers import UvicornWorker

from app.config import setup_config

setup_config()

workers = 4
accesslog = "-"  # to stdout
worker_class = "gunicorn_conf.AppUviconWorker"
loglevel = "debug"

glogging.Logger.datefmt = "%Y-%m-%dT%H:%M:%S"
_format = "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"

glogging.Logger.syslog_fmt = _format
glogging.Logger.access_fmt = _format
glogging.Logger.error_fmt = _format


class AppUviconWorker(UvicornWorker):
    """Create a custom log config for Uvicorn workers"""

    CONFIG_KWARGS = {
        "log_config": "loggingconfig.yml",
    }
