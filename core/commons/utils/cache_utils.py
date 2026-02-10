from django.core.cache import cache

def cache_get_or_set(key, function, timeout=300):
    value = cache.get(key)
    if value:
        return value

    value = function()
    cache.set(key, value, timeout)
    return value

def invalidate_cache(key):
    cache.delete(key)