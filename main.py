import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client
import time

# --- 設定 ---
TABLE_NAME = "ai_song_spotify_ranking"
MIN_POPULARITY = 10

# 認証 (Client Credentials)
# ※403が出る場合、Spotify側でこのClientIDが「検索」を許可されていない状態です。
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
)
sp = spotipy.Spotify(auth_manager=auth_manager)
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def collect_songs(query, market):
    print(f"--- {market} 検索開始 ---")
    try:
        # offsetを0から200まで回して、少しずつ確実に取る
        for offset in range(0, 200, 50):
            # 検索実行
            res = sp.search(q=query, limit=50, offset=offset, type='track', market=market)
            tracks = res.get('tracks', {}).get('items', [])
            
            if not tracks:
                print(f"データがもうありません (offset: {offset})")
                break
                
            print(f"✅ {len(tracks)}件取得成功。保存を開始します...")
            
            for t in tracks:
                if t['popularity'] < MIN_POPULARITY:
                    continue
                
                # スコア判定（Suno, Udioが含まれるか）
                full_text = (t['name'] + t['artists'][0]['name']).lower()
                is_ai = any(k in full_text for k in ['suno', 'udio', 'aiva', 'soundraw'])
                
                if is_ai:
                    data = {
                        "market": market,
                        "popularity": t['popularity'],
                        "ai_score": 100,
                        "name": t['name'],
                        "artist": t['artists'][0]['name'],
                        "release_date": t['album']['release_date'],
                        "url": t['external_urls']['spotify']
                    }
                    supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
            
            time.sleep(1) # インターバル
            
    except Exception as e:
        print(f"❌ エラー発生詳細: {e}")

# 実行
collect_songs('"Suno" OR "Udio"', 'JP')
collect_songs('"Suno" OR "Udio"', 'US')
