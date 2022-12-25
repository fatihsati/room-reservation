import requests


r = requests.get('http://localhost:8000/add?name=deneme')
print(r.status_code)
