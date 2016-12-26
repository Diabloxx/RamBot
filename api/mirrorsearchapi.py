import requests
import json

def search(name=None, page=0, limit=5):
    try:
        request = requests.get("http://m.blosu.net/api/", params={"q" : name, "p" : page, "l" : limit})
    except requests.exceptions.RequestException as e:
        return
    return json.loads(request.text)