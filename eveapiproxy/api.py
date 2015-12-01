import os
import requests
from .base import app, request
from .cache import cache, CACHE_OBJECT_MAX_SIZE

from six.moves.urllib.parse import urlencode
from six import StringIO
from lxml import etree

from time import time, strptime, mktime


API_BASE_URL = os.environ.get('EVE_API_BASE_URL', "https://api.eveonline.com")

HEADERS = {
    'User-Agent': 'Xaroth/eveapiproxy v0.0',
}


class BaseApiCall(object):
    def __init__(self, scope, call):
        self.scope = scope
        self.call = call
        print("New Api Call: %s/%s" % (self.scope, self.call))

    _api_url = None

    @property
    def api_url(self):
        if self._api_url is None:
            self._api_url = "%(base)s/%(scope)s/%(call)s.xml.aspx" % {
                'base': API_BASE_URL,
                'scope': self.scope,
                'call': self.call,
            }
        return self._api_url

    @property
    def request_params(self):
        return dict(self.params)

    @property
    def request_headers(self):
        return HEADERS

    def add_params(self, params):
        self.params = params.items()
        self._cache_key = None
        self.processed = False

    _cache_key = None

    @property
    def cache_key(self):
        if self._cache_key is None:
            self._cache_key = ("%s/%s/%s" % (self.scope, self.call, urlencode(sorted(self.params), doseq=True)))
        return self._cache_key

    cached_until = None
    cached_from = None

    @property
    def time_to_cache(self):
        if self.cached_until and self.cached_from:
            return int(self.cached_until - time())
        return 0

    def parse_content(self, content):
        data = StringIO(content)
        for event, element in etree.iterparse(data, events=["end"]):
            if element.tag not in ("cachedUntil", "currentTime"):
                element.clear()
                continue
            value = strptime(element.text, "%Y-%m-%d %H:%M:%S")
            if element.tag == "cachedUntil":
                self.cached_until = value
            elif element.tag == "currentTime":
                self.cached_from = value
            element.clear()
        self.cached_until = time() + (mktime(self.cached_until) - mktime(self.cached_from))

    def set_content(self, resp):
        self.status_code = resp.status_code
        self.content = resp.content
        self.parse_content(resp.content)
        self.response_headers = {
            'Content-Type': resp.headers.get('content-type', 'application/xml; charset=utf-8'),
        }
        if self.status_code == 200:
            self.response_headers.update({
                'Cache-Control': 'private, max-age=%d' % self.time_to_cache,
            })

    def get(self):
        self.add_params(request.args)
        print("GET call: %d args" % len(request.args))

    def post(self):
        self.add_params(request.form)
        print("POST call: %d args" % len(request.form))

    processed = False

    def process(self):
        resp = requests.post(self.api_url, data=self.request_params, headers=self.request_headers)
        self.set_content(resp)

    @property
    def response(self):
        if not self.processed:
            self.process()
        return self.content, self.status_code, self.response_headers


class CacheApiCall(BaseApiCall):
    from_cache = False

    def process(self):
        obj = cache.get(self.cache_key)
        if obj:
            for key, value in obj.items():
                setattr(self, key, value)
            self.response_headers.update({
                'Cache-Control': 'private, max-age=%d' % self.time_to_cache,
                'X-Cache-Result': 'cached',
            })
        else:
            super(CacheApiCall, self).process()
            self.response_headers.update({
                'X-Cache-Result': 'fetched',
            })
            if len(self.content) > CACHE_OBJECT_MAX_SIZE:
                return
            obj = {}
            for key in ['content', 'status_code', 'response_headers', 'cached_until']:
                obj[key] = getattr(self, key)
            cache.set(self.cache_key, obj, timeout=self.time_to_cache)


class ApiCall(CacheApiCall):
    pass


@app.route('/<scope>/<call>.xml.aspx', methods=['GET', 'POST'])
def api_call(scope, call):
    obj = ApiCall(scope, call)
    if request.method == 'POST':
        obj.post()
    elif request.method == 'GET':
        obj.get()
    return obj.response
