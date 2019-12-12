import sys

if sys.version_info[0] < 3:
    import urlparse
    from urllib import urlencode
else:
    import urllib.parse as urlparse
    from urllib.parse import urlencode


def generate_url(url: str, params: dict):
    parse_result = urlparse.urlparse(url)
    query = dict(urlparse.parse_qsl(parse_result.query))
    query.update(params)
    return urlparse.urlunparse(parse_result._replace(query=urlencode(query)))
