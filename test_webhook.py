import urllib.request
import json
import time

# The endpoint on your local Nginx server that forwards to the Python backend
url = "http://localhost/api/sheets/add"

# Dummy payload reflecting the structure sent from the frontend script.js
payload = {
    "date": time.strftime("%d-%m-%Y"),
    "companyName": "Test Company from Script",
    "pic": "John Doe",
    "position": "Manager",
    "phone": "1234567890",
    "email": "test@example.com",
    "country": "Test Country",
    "city": "Test City",
    "address": "123 Test St, Test City, Test Country",
    "accountExecutive": "Jane Doe",
    "noted": "https://example.com/test-link"
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending test payload to {url}...\n")
print(json.dumps(payload, indent=2))
print("-" * 40)

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        body = response.read().decode('utf-8')
        
        if status_code == 200:
            print("\n✅ SUCCESS! The data was forwarded successfully.")
            print("Check your Google Sheet to see if the row appeared!")
            try:
                print("Response from server:", json.loads(body))
            except:
                print("Response from server:", body)
        else:
            print(f"\n❌ FAILED! The server responded with HTTP {status_code}.")
            print("Response detail:", body)
            
except urllib.error.URLError as e:
    if hasattr(e, 'code'):
        print(f"\n❌ FAILED! The server responded with HTTP {e.code}.")
        print("Response detail:", e.read().decode('utf-8'))
    else:
        print(f"\n❌ CONNECTION ERROR! Could not connect to {url}.")
        print(f"Reason: {e.reason}")
        print("Make sure your Docker containers are running (docker-compose up -d)")
except Exception as e:
    print(f"\n❌ ERROR: An unexpected error occurred: {str(e)}")
