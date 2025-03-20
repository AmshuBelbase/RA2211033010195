import requests
import json

url = "http://20.244.56.144/test/register"

my_data = {
}

response = requests.post(url, json=my_data)

if response.status_code == 200:
    response_data = response.json()

    # Save the response to a JSON file
    with open("response.json", "w") as file:
        json.dump(response_data, file, indent=4)

    print("Response saved to response.json")
else:
    print("Error:", response.status_code, response.text)
