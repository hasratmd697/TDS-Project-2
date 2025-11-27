import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your deployed URL
# Example: https://your-project-name.vercel.app
DEPLOYED_URL = "https://tds-project-2-khaki.vercel.app/"
if not DEPLOYED_URL.endswith("/"):
    DEPLOYED_URL += "/"

ENDPOINT = f"{DEPLOYED_URL}receive_request"

# Get secret from .env or input
SECRET = os.getenv("SECRET")
if not SECRET:
    SECRET = "Hussain"

payload = {
    "email": "24f1002299@ds.study.iitm.ac.in", # Replace with your actual email if needed
    "secret": SECRET,
    "url": "https://tds-llm-analysis.s-anand.net/demo"
}

print(f"Sending request to {ENDPOINT}...")
try:
    response = httpx.post(ENDPOINT, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"An error occurred: {e}")
