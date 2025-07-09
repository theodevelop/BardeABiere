import logging
import os

def setup_logger():
    logger = logging.getLogger("Barde à Bière")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logs/bot.log")
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

logger = setup_logger()
