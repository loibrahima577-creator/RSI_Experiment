import json, os, urllib.request, urllib.error

key = json.load(open(os.path.expanduser("~/.codex/auth.json")))["OPENAI_API_KEY"]
req = urllib.request.Request(
    "https://portdan.com/v1/models",
    headers={"Authorization": "Bearer " + key},
)
try:
    data = json.load(urllib.request.urlopen(req))
    for m in data.get("data", []):
        print(m.get("id"))
except urllib.error.HTTPError as e:
    print("HTTP error", e.code, e.read().decode()[:300])
    