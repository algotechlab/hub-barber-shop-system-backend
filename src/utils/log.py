import logging
import traceback
from datetime import datetime

from src.db.database import db
from src.model.model import Log


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler("src.log")
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


def log_to_db(logger_name: str, level: str, message: str):
    try:
        session = db.session()

        if session.in_transaction():
            session.rollback()

        log_entry = Log(
            timestamp=datetime.utcnow(),
            logger_name=logger_name,
            level=level.upper(),
            message=message,
        )
        session.add(log_entry)
        session.commit()
    except Exception:
        db.session.rollback()
        logger = setup_logger("DBLogger")
        logger.error(traceback.format_exc())


logger = setup_logger("AppLogger")


def logdb(level: str, message: str):
    log_to_db("AppLogger", level, message)
