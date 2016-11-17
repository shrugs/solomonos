import requests
import sys
import re
from os.path import join, dirname
from os import environ as env
from dotenv import load_dotenv
from flask import Flask, request, jsonify

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

SOLO_LOCATION = env.get('SOLO_LOCATION', 'http://localhost:5000')

def solo_request(endpoint, params = {}):
    r = requests.post('{}{}'.format(SOLO_LOCATION, endpoint), params=params)
    print(r.text)
    return jsonify(
        text=r.text,
        response_type='in_channel'
    )

def help_text():
    return """
        /music, by matt@skillshare.com - Control the office speakers!

        /music play
        /music pause
        /music next

        /music play|queue spotify:track:7GhIk7Il098yCjg4BQjzvb

        /music volume up
        /music volume down
        /music volume 11
    """

SLACK_TEAM_TOKEN = env.get('SLACK_TEAM_TOKEN')

HELP_REGEX = re.compile('help$')
PLAY_REGEX = re.compile('play($| (?P<uri>(.*)?))')
QUEUE_REGEX = re.compile('queue($| (?P<uri>(.*)?))')
PAUSE_REGEX = re.compile('pause$')
NEXT_REGEX = re.compile('next$')
VOLUME_REGEX = re.compile('volume($| (?P<volume>[\w|\d]+))')

@app.route('/')
def index():
    return 'ok'

@app.route('/slack', methods=['POST'])
def slack():

    if SLACK_TEAM_TOKEN and request.form['token'] != SLACK_TEAM_TOKEN:
        return 'Unauthorized'

    text = request.form['text']
    m = PLAY_REGEX.match(text)
    if m:
        params = {}
        uri = m.group('uri')
        if uri:
            params['uri'] = uri
        return solo_request('/play', params)

    m = QUEUE_REGEX.match(text)
    if m:
        params = {}
        uri = m.group('uri')
        if uri:
            params['uri'] = uri
        return solo_request('/queue', params)

    m = VOLUME_REGEX.match(text)
    if m:
        params = {}
        volume = m.group('volume')
        if volume:
            params['to'] = volume
        return solo_request('/volume', params)

    m = PAUSE_REGEX.match(text)
    if m:
        return solo_request('/pause')

    m = NEXT_REGEX.match(text)
    if m:
        return solo_request('/next')

    m = HELP_REGEX.match(text)
    if m:
        return help_text()

    return 'I didn\'t understand that.'

if __name__ == '__main__':
    app.run(port=5001)
