import requests

secure_endpoint = "https://example.invalid"
password = "${DEVICE_PASSWORD}"
response = requests.get(secure_endpoint, verify=True)
