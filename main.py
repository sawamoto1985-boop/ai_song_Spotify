import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# 認証設定
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# --- 修正ポイント：tag:newを外し、検索ワードを具体化 ---
# "Suno AI" や "Udio" を含むアーティストや曲名を、人気順（デフォルト）で取得
search_query = '"Suno AI" OR "Udio" OR "AI Generated"'

# 検索実行
results = sp.search(q=search_query, limit=20, type='track')

print(f"--- 抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
print(f"--- 検索クエリ: {search_query} ---")
print("-" * 60)

if results['tracks']['items']:
    for i, track in enumerate(results['tracks']['items']):
        name = track['name']
        artist = track['artists'][0]['name']
        release_date = track['album']['release_date']
        popularity = track['popularity'] 
        url = track['external_urls']['spotify']

        print(f"{i+1:02}. [{release_date}] 人気度:{popularity:2} | {name}")
        print(f"    アーティスト: {artist}")
        print(f"    URL: {url}")
        print("-" * 60)
else:
    print("楽曲が見つかりませんでした。クエリをさらに調整する必要があります。")
