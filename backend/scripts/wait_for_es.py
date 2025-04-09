import time
import requests
from core.config import settings


for i in range(30):
    try:
        response = requests.get(settings.es_hosts[0])
        if response.status_code == 200:
            print("Elasticsearch is ready.")
            break
    except Exception:
        print(f"Waiting for Elasticsearch... attempt {i+1}")
    time.sleep(1)
else:
    raise TimeoutError("Elasticsearch did not start in time")