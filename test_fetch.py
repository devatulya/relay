import urllib.request
import json

url = "http://127.0.0.1:5000/verify-sheet"
data = {"url": "https://docs.google.com/spreadsheets/d/1_bKLZEmmVmLDTrPRq6o1g4T543WUAbeolSeN6q2qx5Q/edit"}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as f:
        print(f.status)
        print(f.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print("Response Body:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Exception: {e}")
