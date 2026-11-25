"""Read-only GLP manifest probe. No credentials, POST, or redirects."""
import json
import urllib.request

URL = "https://www.godlikeproductions.com/ai-forum-api.php?action=manifest"
MAX_BYTES = 262144

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def probe():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(URL, headers={"Accept": "application/json"}, method="GET")
    with opener.open(request, timeout=10) as response:
        if response.status != 200 or response.geturl() != URL:
            raise ValueError("Unexpected response")
        if response.headers.get_content_type() != "application/json":
            raise ValueError("Unexpected content type")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Response too large")
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("ok") is not True or not isinstance(data.get("data"), dict):
        raise ValueError("Unexpected manifest envelope")
    # Connectivity only: inspect protocol fields separately before enabling writes.
    print("Manifest HTTPS GET and JSON envelope verified; publishing not tested.")

if __name__ == "__main__":
    probe()
