import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# 検索ワードを「AI」や「Suno AI」などに設定
search_query = 'AI music' 
results = sp.search(q=search_query, limit=10, type='track')

print(f"--- '{search_query}' の検索結果 上位10曲 ---")
for i, track in enumerate(results['tracks']['items']):
    name = track['name']
    artist = track['artists'][0]['name']
    url = track['external_urls']['spotify']
    print(f"{i+1}: {name} / {artist}")
    print(f"   URL: {url}")
