import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# 1. 環境変数を取得
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# 2. 認証マネージャーを明示的に作成
# これが「トークン」を自動発行してくれます
auth_manager = SpotifyClientCredentials(
    client_id=client_id, 
    client_secret=client_secret
)

# 3. Spotifyクラスの初期化
sp = spotipy.Spotify(auth_manager=auth_manager)

# 4. 検索実行
search_query = '"Suno AI" OR "Udio"'
try:
    results = sp.search(q=search_query, limit=10, type='track')
    
    print(f"--- 抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    if results['tracks']['items']:
        for i, track in enumerate(results['tracks']['items']):
            print(f"{i+1:02}. {track['name']} / {track['artists'][0]['name']}")
    else:
        print("楽曲が見つかりませんでした。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
