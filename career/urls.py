from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def canonical_url(value):
    u = urlsplit(value.strip())
    if u.scheme != 'https' or not u.hostname or u.username or u.password:
        raise ValueError('Use an HTTPS employer URL without credentials')
    query = [(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in {'fbclid','gclid','trk','trackingid'}]
    return urlunsplit(('https',u.netloc.lower(),u.path.rstrip('/') or '/',urlencode(sorted(query)),''))
