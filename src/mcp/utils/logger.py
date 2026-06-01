import logging


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger configured for the application.

    Parameters
    ----------
    name : str
        Name of the calling module

    Returns
    -------
    logging.Logger
        Logger instance
    """

    logger = logging.getLogger(name)

    if not logger.handlers:

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

        logger.setLevel(logging.INFO)
        
        logger.propagate = False

    return logger
