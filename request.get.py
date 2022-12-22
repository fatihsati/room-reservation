import requests


r = requests.get('http://localhost:12000/add?name=deneme')
print(r.text)
