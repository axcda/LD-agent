import requests
import json

# 测试API
url = "http://127.0.0.1:9999/analyze"
data = {
    "content": "def hello():\n    print('Hello, World!')",
    "content_type": "code",
    "context": "Python"
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))