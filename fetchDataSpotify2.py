import requests
import base64
import json

from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Configurable Fields 
CONFIG = {
    "artist": ["id", "name", "popularity", "genres"],
    "track": ["id", "name", "album", "release_date", "popularity", "duration_ms"]
}

# Spotify API Token
def get_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(auth_url, headers=headers, data=data)
    return response.json().get("access_token")

ACCESS_TOKEN = get_access_token()

# Spotify query
def spotify_query(endpoint, params={}):
    url = f"https://api.spotify.com/v1/{endpoint}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_artist_info(artist_name):
    data = spotify_query("search", {"q": artist_name, "type": "artist", "limit": 1})
    
    try:
        artist = data["artists"]["items"][0]
        return {field: artist.get(field, None) for field in CONFIG["artist"]}
    except (IndexError, KeyError):
        print(f"Artist '{artist_name}' not found.")
        return None

# Collaborators form the top tracks
def get__toptracks_artists(artist_id):
    data = spotify_query(f"artists/{artist_id}/top-tracks", {"market": "US"})
    
    featured_artists = {}
    for track in data.get("tracks", []):
        track_info = {
            "title": track["name"],
            "release_date": track["album"]["release_date"],
            "album": track["album"]["name"],
            "popularity": track["popularity"],
            "duration_ms": track["duration_ms"]
        }

        for artist in track["artists"]:
            if artist["id"] != artist_id:
                if artist["id"] not in featured_artists:
                    featured_artists[artist["id"]] = {"name": artist["name"], "songs": []}
                featured_artists[artist["id"]]["songs"].append(track_info)

    return featured_artists

def save_to_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

artist_name = "Dua Lipa"
artist_info = get_artist_info(artist_name)

def get_artist_albums(artist_id):
    albums = []
    params = {"include_groups": "album,single", "limit": 50}
    data = spotify_query(f"artists/{artist_id}/albums", params)
    
    for album in data.get("items", []):
        albums.append({"id": album["id"], "name": album["name"], "release_date": album["release_date"]})
    
    return albums

# --- Get All Tracks from an Album ---
def get_album_tracks(album_id):
    tracks = []
    data = spotify_query(f"albums/{album_id}/tracks", {"limit": 50})

    for track in data.get("items", []):
        tracks.append({"id": track["id"], "name": track["name"], "artists": track["artists"]})

    return tracks

# Not just top tracks, but all collaborations. TODO: Set some rules of what to exclude, e.g. Remixes, songs without release date. 
def get_all_collaborations(artist_id):
    albums = get_artist_albums(artist_id)
    collaborations = {}

    for album in albums:
        album_tracks = get_album_tracks(album["id"])

        for track in album_tracks:
            track_info = {
                "title": track["name"],
                "release_date": album["release_date"],
                "album": album["name"]
            }

            for artist in track["artists"]:
                if artist["id"] != artist_id:  
                    if artist["id"] not in collaborations:
                        collaborations[artist["id"]] = {"name": artist["name"], "songs": []}
                    collaborations[artist["id"]]["songs"].append(track_info)

    return collaborations

if artist_info:
    artist_id = artist_info["id"]
    collaborators = get_all_collaborations(artist_id)
    
    
    data_to_save = {
        artist_id: {
            "name": artist_info["name"],
            "popularity": artist_info["popularity"],
            "genres": artist_info["genres"],
            "collaborators": collaborators
        }
    }
    
    save_to_json("spotify_graph.json", data_to_save)
    print("Data saved to spotify_graph.json")
