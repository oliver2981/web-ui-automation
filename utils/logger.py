# 统一的日志封装:让每个页面对象都有一致的日志输出
import logging


def get_logger(name: str) -> logging.Logger:
    """按名称获取一个带格式的 logger。重复调用不会重复添加 handler。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
