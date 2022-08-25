#!/usr/bin/env python3
import toml
import json
import http.client

creds = toml.load('credentials.toml').get('keys')
CIRCLE_TOKEN = creds.get('circleci_token')
CIRCLECI_ORG_SLUG = creds.get('circleci_org_slug')
CIRCLECI_ORG_ID = creds.get('circleci_org_id')
CIRCLECI_BASE_URL = "http://circleci.com/api/v2"
CIRCLECI_CONTEXT_NAME = "cicd-workshop"

SNYK_TOKEN = creds.get('snyk_token')
DOCKER_USERNAME = creds.get('docker_login')
DOCKER_TOKEN = creds.get('docker_token')
TF_CLOUD_KEY = creds.get('tf_cloud_key')
DIGITALOCEAN_TOKEN = creds.get('digitalocean_token')

# Assuming we always return JSON
def circleci_api_request(method, endpoint, payload_dict):
  conn = http.client.HTTPSConnection("circleci.com")
  headers = {
    'content-type': "application/json",
    'Circle-Token': CIRCLE_TOKEN
  }
  conn.request(method, f'/api/v2/{endpoint}', json.dumps(payload_dict), headers)
  
  res = conn.getresponse()
  data = res.read()
  data_str = data.decode("utf-8")
  return json.loads(data_str)

def add_circle_token_to_context(context_id, env_var_name, env_var_value):
  return circleci_api_request("PUT", f'context/{context_id}/environment-variable/{env_var_name}', { "value": env_var_value })

# Get the context id to which we'll store env vars

# First check whether the context named cicd-workshop
contexts = circleci_api_request("GET", f'context?owner-id={CIRCLECI_ORG_ID}&owner-type=organization', None).get('items')
context = next(ctx for ctx in contexts if ctx.get('name') == CIRCLECI_CONTEXT_NAME)

if context == None:
  # Context doesn't exist so we create it   
  context_payload = {
    "name": CIRCLECI_CONTEXT_NAME,
      "owner": {
        "id": CIRCLECI_ORG_ID,
        "type": "organization"
      }
  }
  context = circleci_api_request("POST", f'context', context_payload)
  
circleci_context_id = context.get("id")

# Add Env vars to context
print(add_circle_token_to_context(circleci_context_id, "SNYK_TOKEN", SNYK_TOKEN))
print(add_circle_token_to_context(circleci_context_id, "DOCKER_LOGIN", DOCKER_USERNAME))
print(add_circle_token_to_context(circleci_context_id, "DOCKER_PASSWORD", DOCKER_TOKEN))
print(add_circle_token_to_context(circleci_context_id, "TF_CLOUD_KEY", TF_CLOUD_KEY))
print(add_circle_token_to_context(circleci_context_id, "DIGITALOCEAN_TOKEN", DIGITALOCEAN_TOKEN))

# TODO: add other necessary env vars???