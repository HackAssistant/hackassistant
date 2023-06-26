from django.core.cache import cache
from django.utils import timezone


# 5 min cache
def cache_tables(func):
    def wrapper(*args, **kwargs):
        result = cache.get(func.__qualname__)
        if result is None or kwargs.get('force_update', False):
            try:
                del kwargs['force_update']
            except KeyError:
                pass
            result = func(*args, **kwargs)
            cache.set(func.__qualname__, result, 300)
            cache.set(func.__qualname__ + '_exp_time', timezone.now(), 300)

        return result

    def get_cache_time():
        exp = cache.get(str(func.__qualname__) + '_exp_time')
        return (timezone.now() - exp).seconds // 60

    wrapper.get_cache_time = get_cache_time
    return wrapper
