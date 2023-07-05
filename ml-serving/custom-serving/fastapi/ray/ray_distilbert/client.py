import requests

prompt = "This was a masterpiece. Not completely faithful to the books, but enthralling from beginning to end. Might be my favorite of the three."
input = "%20".join(prompt.split(" "))
resp = requests.get(f"http://127.0.0.1:8000/classify?sentence={prompt}")
print(resp.status_code, resp.json())
