import os
import socket
import sys

import spotipy
from flask import Flask
from redis import Redis, RedisError
from spotipy.oauth2 import SpotifyClientCredentials

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

client_credentials_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager)


@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)


@app.route("/list")
def list():

    user = 'newjeffersonsilveira'

    if len(sys.argv) > 1:
        user = sys.argv[1]
    playlists = spotify.user_playlists(user)

    row = ""
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            row += ("{\"num\":%4d, \"uri\":\"%s\", \"name\":\"%s\"}," %
                    (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = spotify.next(playlists)
        else:
            playlists = None
    json = "{row}"
    return json.format(row=row)


@app.route("/search")
def search():
    row = spotify.search(q='artist:' + 'wazer', type='artist')

    json = "{row}"
    return json.format(row=row)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
