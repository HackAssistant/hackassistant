from datetime import datetime

from django.core.cache import cache


# 10 min cache
def cache_stats(func):
    def wrapper(*args, **kwargs):
        result = cache.get(func.__qualname__ + args[-1])
        if result is None or kwargs.get('force_update', False):
            try:
                del kwargs['force_update']
            except KeyError:
                pass
            result = func(*args, **kwargs)
            cache.set(func.__qualname__ + args[-1], result, 600)
            cache.set(func.__qualname__ + args[-1] + '_exp_time', datetime.now(), 600)

        return result

    def get_cache_time(*args, **kwargs):
        exp = cache.get(str(func.__qualname__) + (args[0] if len(args) > 0 else kwargs['model_name']) + '_exp_time')
        return (datetime.now() - exp).seconds // 60

    wrapper.get_cache_time = get_cache_time
    return wrapper
