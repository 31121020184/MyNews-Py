import json
import urllib.request

DEFAULT_ENCODING ='utf-8'
url ='http://127.0.0.1:8000/api/stories/'

urlResponse =urllib.request.urlopen(url)

if hasattr(urlResponse.headers,'get_content_charset'):
    endcoding = urlResponse.headers.get_content_charset(DEFAULT_ENCODING)
else:
     endcoding = urlResponse.headers.getparam('charset') or DEFAULT_ENCODING

stories = json.loads(urlResponse.read().decode(endcoding))

results = stories['results']
for item in results:
      print(item['url'])

