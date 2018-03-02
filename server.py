import os
import json
from flask import Flask, request
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

ACCOUNT_SID = 'AC0df3bf80183839dd04a878cd8d2fc7d8'
AUTH_TOKEN = '6f0e48991622bf6008e99a7107fd039b'
API_KEY = 'SK0e0f65b197b8f8176ffa754f230cc781'
API_KEY_SECRET = 'ujKTh7hL8WwX9QkGahsHc8KK5HeIPuOg'
PUSH_CREDENTIAL_SID_IOS_DEV = 'CRd76831eec29b5ade0eb0030e43ad8e36'
PUSH_CREDENTIAL_SID_IOS_PROD = 'CRefeddc2f2208366236953589c6f7d0ab'
PUSH_CREDENTIAL_SID_ANDROID = 'CRb0a1441bf89b5256d80328bef0950f6a'
APP_SID = 'AP59ba55fdf50642936a29e04dbe3fe799'

"""
Use a valid Twilio number by adding to your account via https://www.twilio.com/console/phone-numbers/verified
"""
CALLER_NUMBER = '1234567890'

"""
The caller id used when a client is dialed.
"""
CALLER_ID = 'client:quick_start'
IDENTITY = 'alice'


app = Flask(__name__)

"""
Creates an access token with VoiceGrant using your Twilio credentials.
"""
@app.route('/accessToken', methods=['GET', 'POST'])
def token():
  client_name = request.values.get('client')
  platform = request.values.get('platform')
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  app_sid = os.environ.get("APP_SID", APP_SID)
  
  if platform == 'iosdev':
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_IOS", PUSH_CREDENTIAL_SID_IOS_DEV)
  elif platform == 'iosprod':
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_IOS", PUSH_CREDENTIAL_SID_IOS_PROD)
  else:
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_ANDROID", PUSH_CREDENTIAL_SID_ANDROID)
    
  if client_name:
     IDENTITY =client_name
  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  token = AccessToken(account_sid, api_key, api_key_secret, identity=IDENTITY)
  token.add_grant(grant)
  k = {'accessToken': str(token)}
  return json.dumps(k)

"""
Creates an endpoint that plays back a greeting.
"""
@app.route('/incoming', methods=['GET', 'POST'])
def incoming():
  resp = VoiceResponse()
  resp.say("Congratulations! You have received your first inbound call! Good bye.")
  return str(resp)

"""
Makes a call to the specified client using the Twilio REST API.
"""
@app.route('/placeCall', methods=['GET', 'POST'])
def placeCall():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  to = request.values.get("to")
  call = None

  if to is None or len(to) == 0:
    call = client.calls.create(url=request.url_root + 'incoming', to='client:' + IDENTITY, from_=CALLER_ID)
  elif to[0] in "+1234567890" and (len(to) == 1 or to[1:].isdigit()):
    call = client.calls.create(url=request.url_root + 'incoming', to=to, from_=CALLER_NUMBER)
  else:
    call = client.calls.create(url=request.url_root + 'incoming', to='client:' + to, from_=CALLER_ID)
  return str(call)

"""
Creates an endpoint that can be used in your TwiML App as the Voice Request Url.
In order to make an outgoing call using Twilio Voice SDK, you need to provide a
TwiML App SID in the Access Token. You can run your server, make it publicly
accessible and use `/makeCall` endpoint as the Voice Request Url in your TwiML App.
"""
@app.route('/makeCall', methods=['GET', 'POST'])
def makeCall():
  resp = VoiceResponse()
  to = request.values.get("to")

  if to is None or len(to) == 0:
    resp.say("Congratulations! You have just made your first call! Good bye.")
  elif to[0] in "+1234567890" and (len(to) == 1 or to[1:].isdigit()):
    resp.dial(callerId=CALLER_NUMBER).number(to)
  else:
    resp.dial(callerId=CALLER_ID).client(to)
  return str(resp)

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = VoiceResponse()
  resp.say("Welcome to Twilio")
  return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
