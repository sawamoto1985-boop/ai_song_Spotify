import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# 1. 認証設定
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# 2. プロ仕様の検索クエリ設定
# tag:new -> 最近リリースされた曲に絞る
# "Suno" OR "Udio" -> 代表的なAI生成ツールの名前を含むもの
# -King -Queen -> 有名アーティストが混ざるのを防ぐための除外（マイナス検索）
search_query = 'tag:new "Suno" OR "Udio" -King -Queen'

# 3. 検索実行（上位20件、新しい順を意識）
results = sp.search(q=search_query, limit=20, type='track')

# 4. 結果の出力
print(f"--- 抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
print(f"--- プロ仕様クエリ: {search_query} ---")
print("-" * 60)

if results['tracks']['items']:
    for i, track in enumerate(results['tracks']['items']):
        # 曲の基本情報
        name = track['name']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        release_date = track['album']['release_date']
        popularity = track['popularity'] # 0-100の人気指標
        url = track['external_urls']['spotify']

        # 表示フォーマット
        print(f"{i+1:02}. [{release_date}] 人気度:{popularity:2} | {name}")
        print(f"    アーティスト: {artist} / アルバム: {album}")
        print(f"    URL: {url}")
        print("-" * 60)
else:
    print("条件に合う最新のAI楽曲は見つかりませんでした。")
