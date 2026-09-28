import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("PEXELS_API_KEY")
headers = {"Authorization": key}

queries = [
    "cute baby kitten",
    "cute ginger kitten",
    "cute fluffy rabbit",
    "cute small puppy",
    "fresh strawberry macro",
    "fruits splash animation",
    "3d animation cute"
]

for q in queries:
    url = f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page=3"
    r = requests.get(url, headers=headers)
    vids = r.json().get("videos", [])
    print(f"Query '{q}': found {len(vids)} vertical HD videos")
