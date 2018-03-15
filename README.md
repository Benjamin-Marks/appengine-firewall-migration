# appengine-firewall-migration
Migrate a Google App Engine app's DoS API Config to the App Engine Firewall

Dependencies:
 - PyYaml
 - Requests
 - oauth2client
 
The App Engine app in question will also need to have enabled the App Engine Admin API, and have an OAuth2Client id/secret, inserted into the appropriate vars at the top of the script.
