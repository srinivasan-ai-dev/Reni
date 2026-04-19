import requests
import sys

try:
    with open('test.jpg', 'wb') as f:
        f.write(b'test')
    
    files = {'file': open('test.jpg', 'rb')}
    r = requests.post('http://127.0.0.1:8000/api/v1/investigate', files=files)
    print("STATUS", r.status_code)
    data = r.json()
    print("KEYS", data.keys())
    print("FUSION_RESULT", data.get('fusion_result'))
except Exception as e:
    print("Error:", e)
