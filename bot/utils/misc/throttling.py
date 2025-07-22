def rate_limit(limit: float, key: str = None):
    """
    Aiogram 3.x handlerlar uchun rate limit dekoratori.

    :param limit: sekundlardagi cheklov
    :param key: maxsus throttling kaliti (ixtiyoriy)
    """
    def decorator(handler):
        setattr(handler, 'rate_limit', limit)
        if key:
            setattr(handler, 'rate_limit_key', key)
        return handler

    return decorator
