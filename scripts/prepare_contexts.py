#!/usr/bin/env python3
import toml
import requests
import json

creds = toml.load('credentials.toml').get('keys')
print(creds)

# print(creds.circleci_token)
# print(creds["circleci_token"])
# print(creds.get('keys').get('circleci_token'))

circleci_token = creds.get('circleci_token')
circleci_org_slug = creds.get('circleci_org_slug')

docker_login = creds.get('docker_login')
docker_pw = creds.get('docker_pw')


CIRCLECI_BASE_URL = "http://circleci.com/api/v2"
CIRCLECI_CONTEXT_NAME = "cicd-workshop"


payload = {
    "name": CIRCLECI_CONTEXT_NAME,
    "owner": {
        "slug": circleci_org_slug,
        "type": "organization"
    }
}


# payload = "{\n    \"name\": {{CIRCLE_CONTEXT_NAME}},\n    \"owner\": {\n        \"slug\": {{ORG_SLUG}},\n        \"type\": \"organization\"\n    }\n}"
headers = {
  'Circle-Token': circleci_token,
  'Content-Type': 'application/json'
}

print(payload)
# print(headers)

response = requests.request("POST", CIRCLECI_BASE_URL+"/context", headers=headers, json=payload)

print(response.status_code)
print(response.json())

# Get CircleCI org type?
# Create Context for CircleCI

# Create token for Docker

# Add env variable for Snyk token
# Add env variable for Docker token
# Add env variable for DO token

# Add env variable(s) for AWS creds