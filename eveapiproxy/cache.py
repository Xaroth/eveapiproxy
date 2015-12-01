import os
import sys
from six import text_type

ENV = os.environ


class DefaultCache(object):
    DISABLED = True

    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def set(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def get_many(self, *args, **kwargs):
        return {}

    def set_many(self, *args, **kwargs):
        pass

    def delete_many(self, *args, **kwargs):
        pass

try:
    from flask.ext.cache import Cache
except ImportError:
    Cache = DefaultCache

from .base import app

CACHE_TYPE = ENV.get('EVE_API_CACHE_TYPE', None)
if CACHE_TYPE in (None, 'none', ''):
    Cache = DefaultCache
    CACHE_TYPE = ''
else:
    print("Using cache strategy: %s" % CACHE_TYPE)


def tolist(x):
    return text_type(x).split(',')


env_keys = [
    ('CACHE_TYPE', text_type),
    ('CACHE_MEMCACHED_SERVERS', tolist),
    ('CACHE_MEMCACHED_USERNAME', text_type),
    ('CACHE_MEMCACHED_PASSWORD', text_type),
    ('CACHE_REDIS_HOST', text_type),
    ('CACHE_REDIS_PORT', int),
    ('CACHE_REDIS_PASSWORD', text_type),
    ('CACHE_REDIS_DB', text_type),
    ('CACHE_DIR', text_type),
    ('CACHE_REDIS_URL', text_type),
    ('CACHE_DEFAULT_TIMEOUT', int),
    ('CACHE_THRESHOLD', int),
    ('CACHE_KEY_PREFIX', text_type),
    ('CACHE_OBJECT_MAX_SIZE', int),
]
defaults = {
    'CACHE_KEY_PREFIX': 'apiproxy:',
    'CACHE_OBJECT_MAX_SIZE': (1000 ** 2) * 5
}
if CACHE_TYPE.endswith("memcached"):
    defaults.update({
        'CACHE_MEMCACHED_SERVERS': ['127.0.0.1:11211'],
        'CACHE_OBJECT_MAX_SIZE': (1000 ** 2) * 1
    })

config = defaults.copy()
for key, trans in env_keys:
    envvar = ENV.get('EVE_API_%s' % key, None)
    if not envvar:
        continue
    try:
        envvar = trans(envvar)
    except:
        sys.stderr.write("The environment variable 'EVE_API_%s' is malformed: %r'" % (key, envvar))
        continue
    config[key] = envvar

CACHE_OBJECT_MAX_SIZE = config.pop('CACHE_OBJECT_MAX_SIZE')
cache = Cache(app, config=config)
