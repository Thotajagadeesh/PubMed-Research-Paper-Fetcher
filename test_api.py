import json
import requests

url = "https://jsonplaceholder.typicode.com/posts/1"  # Public API
response = requests.get(url)  # Making a GET request

if response.status_code == 200:
    response_json = response.json()  # Extract JSON
    formatted_json = json.dumps(response_json, indent=4)  # Pretty print JSON
    print(formatted_json)

    # Save to a file
    with open("response.json", "w") as file:
        json.dump(response_json, file, indent=4)

else:
    print(f"Error: {response.status_code}")
