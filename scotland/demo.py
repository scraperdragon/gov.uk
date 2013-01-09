import requests
import requests_cache

requests_cache.configure()
requests.get('http://httpbin.org')
