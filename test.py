import requests
import json

api_endpoint = 'http://localhost:5000/api/predictBurnOut'

# Mock designation variable
designation = 1

# Create a dictionary with two integer values
json_data = {'Designation': designation, 'WFH Setup Available': 'No', 'Resource Allocation': 1.0, 'Mental Fatigue Score': 1.8}

# Convert the dictionary to a JSON string
json_payload = json.dumps(json_data)

# Set the Content-Type header to indicate JSON data
headers = {'Content-Type': 'application/json'}

# Make a POST request to the Flask API endpoint with JSON payload
response = requests.post(api_endpoint, data=json_payload, headers=headers)

# Print the response
print('Response Status Code:', response.status_code)
try:
    response_json = response.json()
    print('Response JSON:', json.dumps(response_json, indent=2))
except ValueError:
    print('Response Content:', response.text)

api_endpoint = 'http://localhost:5000/api/generateTeam'

csv_file_path = 'test.csv'

# Create FormData-like structure
files = {'csv_file': ('test.csv', open(csv_file_path, 'rb'), 'text/csv')}
data = {'Designation': str(designation)}

# Make a POST request to the Flask API endpoint
response = requests.post(api_endpoint, files=files, data=data)

# Print the response
print('Response Status Code:', response.status_code)
try:
    response_json = response.json()
    print('Response JSON:', json.dumps(response_json, indent=2))
except ValueError:
    print('Response Content:', response.text)