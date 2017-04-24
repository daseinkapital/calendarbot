# calendarbot
Calendarbot is a Slackbot that I made to display events for the Institute of Industrial and Systems Engineers at Virginia Tech by pulling information from our Google Calendar

If you want to adapt this script, it's not too hard. You will need to have a file called 'client_secret.json' which has:
```
{
  "installed": {
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "client_email": "",
    "redirect_uris": [
      "urn:ietf:wg:oauth:2.0:oob",
      "oob"
    ],
    "client_x509_cert_url": "",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
  }
}
```
with the client_id and client_secret filled out. This can be found at https://console.developers.google.com/apis

Change up the logic in the calendar_call.py to whatever your project may need. Also reference the slack docs on creating a bot to get started.
