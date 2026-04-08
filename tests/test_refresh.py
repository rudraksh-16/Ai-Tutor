import requests
import string
import random

BASE = "http://localhost:8000"

rand_str = ''.join(random.choices(string.ascii_lowercase, k=8))
email = f"test_{rand_str}@example.com"
pw = "Test@123"

# Register
requests.post(f"{BASE}/api/auth/register", json={"name": "Refresh Tester", "email": email, "password": pw})

# Login
resp = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": pw})
data = resp.json()

acc = data.get("access_token")
ref = data.get("refresh_token")

print(f"Tokens obtained. Refresh: {ref[:15]}...")

# Refresh
refresh_resp = requests.post(f"{BASE}/api/auth/refresh", json={"refresh_token": ref})
new_data = refresh_resp.json()

new_acc = new_data.get("access_token")
print(f"Refresh response status: {refresh_resp.status_code}")
if new_acc and new_acc != acc:
    print("SUCCESS: Got new access token")
else:
    print(f"FAIL: {new_data}")
