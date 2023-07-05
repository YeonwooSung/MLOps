import requests

image_url = "https://ultralytics.com/images/zidane.jpg"
resp = requests.get(f"http://127.0.0.1:8000/detect?image_url={image_url}")

with open("output.jpeg", 'wb') as f:
    f.write(resp.content)
