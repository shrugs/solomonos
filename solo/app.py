from urllib import quote_plus
from os.path import join, dirname
from os import environ as env
from dotenv import load_dotenv
from flask import Flask, request
import soco

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

player_name = env.get('PLAYER_NAME', 'SONOS')

def get_player():
    zones = soco.discover()
    if not zones:
        print 'No zones :('
        return None
    the_zones = [zone for zone in zones if zone.player_name == player_name]
    if len(the_zones) > 0:
        return the_zones[0]

    return None

def format_uri(uri):
    return 'x-sonos-spotify:{}?sid=12&flags=8224&sn=15'.format(quote_plus(uri))

@app.route('/')
def index():
    return 'ok'

@app.route('/play', methods=['POST'])
def play():
    # play <?song>
    player = get_player()
    if not player:
        return "no player :'("

    song_uri = request.args.get('uri')
    if song_uri:
        player.play_uri(format_uri(song_uri))
    else:
        player.play()
    return 'Playing!'

@app.route('/queue', methods=['POST'])
def queue():
    # play <?song>
    player = get_player()
    if not player:
        return "no player :'("

    song_uri = request.args.get('uri')
    if not song_uri:
        return 'I need a song to queue'

    player.add_uri_to_queue(format_uri(song_uri))
    return 'Queued!'

@app.route('/pause', methods=['POST'])
def pause():
    player = get_player()
    if not player:
        return "no player :'("

    player.pause()
    return 'Paused!'


@app.route('/volume', methods=['POST'])
def volume():
    # volume up|down|:number
    player = get_player()
    if not player:
        return "no player :'("

    to_volume = request.args.get('to')
    if not to_volume:
        return 'Current Volume: {}'.format(player.volume)

    if to_volume == 'up':
        player.volume = player.volume + 1
    elif to_volume == 'down':
        player.volume = player.volume - 1
    else:
        to_volume = int(to_volume)
        player.volume = to_volume

    return 'Changed Volume!'

@app.route('/next', methods=['POST'])
def next_song():
    player = get_player()
    if not player:
        return "no player :'("

    player.next()
    return 'Next Song!'

if __name__ == '__main__':
    app.run(port=5000)
