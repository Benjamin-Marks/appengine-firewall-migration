# Required packages:
#   yaml: https://github.com/yaml/pyyaml
#   requests: https://github.com/requests/requests
#   oauth2client: https://github.com/google/oauth2client

import json
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import requests
import yaml


# The path to the dos.yaml file
FILE = 'dos.yaml'
# The cloud project id to update
PROJECT = 'myProject'
# This information is taken from Google Cloud Constole. To create your
# own OAuth Client for your project, go to
# console.cloud.google.com/?project=PROJECT > API Manager > Credentials,
# and follow the steps there.
# Ensure the client has an authorized redirect_uri of http://localhost:8080
# Ensure you have the Admin API enabled on your project
# (Cloud Console > API Manager > Dashboard > Enable APIs and Services
#  > Google App Engine Admin API)
CLIENT_ID = 'id'
CLIENT_SECRET = 'secret'

# Priority to begin inserting dos rules
MAX_PRIORITY = 2147483646

# Get an access token to authenticate our request.
flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=
    'https://www.googleapis.com/auth/appengine.admin https://www.googleapis.com/auth/cloud-platform',
    redirect_uri='http://example.com/oauth2callback')
storage = Storage('creds.data')
credentials = run_flow(flow, storage)
credentials = storage.get()

# Fetch the app's firewall config.
url = 'https://appengine.googleapis.com/v1/apps/{}/firewall/ingressRules?pageSize=1000'.format(
    PROJECT)
response = requests.get(
    url, headers={'Authorization': 'Bearer ' + credentials.access_token})
if (response.status_code != requests.codes.ok):
  print('Bad response. Could not retrieve firewall config.')
  exit()
firewall_json = response.json()

print('Original Firewall Config:')
print(json.dumps(firewall_json))

# Add our DoS API Rules.
# Parse the dos.yaml config.
print('Load dos.yaml config from: ' + FILE)
with open(FILE, 'r') as stream:
  try:
    dos_config = yaml.load(stream)
  except yaml.YAMLError as exc:
    print(exc)
    exit()
# Append the DoS Rules to the Firewall config.
# N.B. this does not check for duplicate priorities.
for i in xrange(len(dos_config['blacklist'])):
  firewall_json['ingressRules'].append({
      'priority': MAX_PRIORITY - i,
      'action': 'DENY',
      'sourceRange': dos_config['blacklist'][i]['subnet'],
      'description': dos_config['blacklist'][i]['description']
  })

print('Attempting to update firewall config to')
print(json.dumps(firewall_json))
# Batch update firewall rules.
url = 'https://appengine.googleapis.com/v1/apps/{}/firewall/ingressRules:batchUpdate'.format(
    PROJECT)
response = requests.post(
    url,
    data=json.dumps(firewall_json),
    headers={'Authorization': 'Bearer ' + credentials.access_token})
if (response.status_code != requests.codes.ok):
  print('Bad response. Firewall not updated.')
  exit()

print('Firewall config is now: ')
print(json.dumps(response.json()))
