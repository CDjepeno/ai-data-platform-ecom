import logging

def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger configuré pour l'application.

    Parameters
    ----------
    name : str
        Nom du module appelant

    Returns
    -------
    logging.Logger
        Instance du logger
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